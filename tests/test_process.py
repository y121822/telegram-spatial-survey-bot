import boto3
from unittest import mock, main
from moto import mock_s3
from engine.process import State, Survey, PointPolygon, QuestionAnswer, Coord, Media, Delete, CreateWebMap, \
    CreateGJsonShp, GeoJson, Shp
from engine.utils.tables import Tables
from engine.utils.answers import answers
from tests.utils.utils import RunAllTestCase, ShpProcess, Message
from tests.utils.set import SetTestData
from tests.utils.data import Data, Result


# Drop and create tables in the testing mode
tables = Tables('test_')
tables.drop()
tables.create()

# The database connection
connection = tables.connection
cursor = tables.cursor

# Instances of process classes in the testing mode
state, delete, survey = State('test_'), Delete('test_'), Survey('test_')
coord, media, qa = Coord('test_'), Media('test_'), QuestionAnswer('test_')
pp, webmap, gjson_shp = PointPolygon(), CreateWebMap('test_'), CreateGJsonShp('test_')
gjson, shp = GeoJson('test_'), Shp('test_')


class TestState(RunAllTestCase, Message, Result):
    """Test State class in
       process.py"""
    def test_states(self):
        self.expectEqual(state.states, self.result_states)

    def test_show_state_init(self):
        self.num = 1

        self.expectEqual(state.show_state(self.message), self.result_states['INIT'])

    def test_show_state(self):
        self.num = 2

        cursor.execute(f"insert into test_user_state values({self.message.from_user.id},"
                       f"'{self.message.from_user.first_name}', {self.data_states['RESULT']})")
        connection.commit()

        self.expectEqual(state.show_state(self.message), self.result_states['RESULT'])

    def test_save_state(self):
        self.num = 3

        cursor.execute(f"insert into test_user_state values({self.message.from_user.id}, "
                       f"'{self.message.from_user.first_name}', {self.data_states['TRANSIT']})")
        connection.commit()

        state.save_state(self.message, self.data_states['SUBMIT'])

        cursor.execute(f'select user_state from test_user_state where user_id = {self.message.from_user.id}')
        self.expectEqual(cursor.fetchall()[0][0], self.result_states['SUBMIT'])


class SurveyTest(RunAllTestCase, Message, Result):
    """Test Survey class in
       process.py"""
    def test_save_survey(self):
        self.num = 4

        cursor.execute(f"insert into test_user_state values({self.message.from_user.id}, "
                       f"'{self.message.from_user.first_name}')")
        connection.commit()

        for i in range(1, 10):
            self.text = f"{self.message.survey}'" * i
            if 0 < i < 4:
                survey.save_survey(self.message)
                cursor.execute(f"select survey from test_user_state where user_id = {self.message.from_user.id}")
                self.expectEqual(cursor.fetchall()[0][0], self.result_save_survey[i])
            else:
                self.expectTrue(survey.save_survey(self.message))

    def test_get_survey(self):
        self.num = 5

        cursor.execute(f"insert into test_user_state(user_id, survey) values({self.message.from_user.id}, "
                       f"'{self.message.survey}')")
        connection.commit()

        self.expectEqual(survey.get_survey(self.message), self.message.survey)

    @mock.patch('engine.process.Survey.get_survey')
    def test_get_author(self, get_survey):
        self.num = 6

        get_survey.return_value = self.message.survey

        cursor.execute(f"insert into test_questions(survey, author) values('{self.message.survey}', "
                       f"{self.message.from_user.id})")
        connection.commit()

        self.expectEqual(survey.get_author(self.message), self.message.from_user.id)

    def test_survey_initial(self):
        self.num = 7

        self.text = f"{self.message.survey}'"
        self.expectEqual(survey.survey_initial(self.message), answers['SURVEY_SAVED'] % f'{self.message.survey}`')

        cursor.execute(f"select survey, author, question from test_questions where id = (select max(id) from "
                       f"test_questions where survey = '{self.message.survey}`')")
        self.expectEqual(cursor.fetchall()[0], (f'{self.message.survey}`', self.message.from_user.id, None))

    @mock.patch('engine.process.Survey.get_survey')
    def test_survey_next(self, get_survey):
        self.num = 8

        get_survey.return_value = self.message.survey

        cursor.execute(f"insert into test_questions(survey, author, question) values('{self.message.survey}', "
                       f"{self.message.from_user.id}, 'question{self.num}')")
        connection.commit()

        survey.survey_next(self.message)

        cursor.execute(f"select survey, author, question from test_questions where id = (select max(id) from "
                       f"test_questions where survey = '{self.message.survey}')")
        self.expectEqual(cursor.fetchall()[0], (self.message.survey, self.message.from_user.id, None))

    def test_survey_check(self):
        self.num = 9

        cursor.execute(f"insert into test_questions(survey, author, question) values('{self.message.survey}`', "
                       f"{self.message.from_user.id}, 'question{self.num}')")
        connection.commit()

        self.text = f"{self.message.survey}'"

        self.expectTrue(survey.survey_check(self.message))

        cursor.execute(f"delete from test_questions where survey = '{self.message.survey}`'")
        connection.commit()

        self.expectFalse(survey.survey_check(self.message))

        self.text = self.text * 4

        self.expectFalse(survey.survey_check(self.message))


class PointPolygonTest(RunAllTestCase, Data, Result):
    """Test PointPolygon class in
       process.py"""
    def test_point(self):
        self.expectEqual(pp.point(self.data_point), self.result_point)

    def test_polygon(self):
        self.expectEqual(pp.polygon(self.data_polygon), self.result_polygon)


class QuestionAnswerTest(RunAllTestCase, Message, Result):
    """Test QuestionAnswer class in
       process.py"""
    @mock.patch('engine.process.Survey.get_survey')
    def test_ans_check_(self, get_survey):
        self.num = 10

        get_survey.return_value = self.message.survey

        cursor.execute(f"insert into test_features(user_id, survey, ans_check) values({self.message.from_user.id}, "
                       f"'{self.message.survey}', {self.data_ans_check[0]})")
        connection.commit()

        self.expectTrue(qa.ans_check(self.message))

        cursor.execute(f"delete from test_features where survey = '{self.message.survey}'")
        cursor.execute(f"insert into test_features(user_id, survey, ans_check) values({self.message.from_user.id}, "
                       f"'{self.message.survey}', {self.data_ans_check[1]})")
        connection.commit()

        self.expectFalse(qa.ans_check(self.message))

    @mock.patch('engine.process.Survey.get_survey')
    def test_init_row(self, get_survey):
        self.num = 11

        get_survey.return_value = self.message.survey

        qa.init_row(self.message)

        cursor.execute(f"select user_id, user_name, survey from test_features where id = (select max(id) from "
                       f"test_features where survey = '{self.message.survey}')")
        self.expectEqual(cursor.fetchall()[0], (self.message.from_user.id, self.message.from_user.first_name,
                                                self.message.survey))

    @mock.patch('engine.process.Survey.get_survey')
    def test_question_insert(self, get_survey):
        self.num = 12

        get_survey.return_value = self.message.survey

        self.text = f"question{self.num}'"

        cursor.execute(f"insert into test_questions (id, survey, author) values (default, '{self.message.survey}',"
                       f"{self.message.from_user.id})")
        connection.commit()

        self.expectEqual(qa.question_insert(self.message), answers['Q_SAVED'] % f'{self.message.text[:-1]}`')

        cursor.execute(f"select question from test_questions where id = (select max(id) from "
                       f"test_questions where survey = '{self.message.survey}')")
        self.expectEqual(cursor.fetchall()[0][0], f'{self.message.text[:-1]}`')

        self.expectFalse(qa.question_insert(self.message))

        self.text = self.text * 5

        cursor.execute(f"update test_questions set question = null where id = (select max(id) from test_questions "
                       f"where survey = '{self.message.survey}')")
        connection.commit()

        self.expectEqual(qa.question_insert(self.message), answers['LONG'])

    @mock.patch('engine.process.Survey.get_survey')
    def test_question_null(self, get_survey):
        self.num = 13

        get_survey.return_value = self.message.survey

        self.text = f'question{self.num}'

        cursor.execute(f"insert into test_questions (id, survey, author, question) values (default, "
                       f"'{self.message.survey}', {self.message.from_user.id}, '{self.message.text}')")
        connection.commit()

        qa.question_null(self.message)

        cursor.execute(f"select question from test_questions where id = (select max(id) from "
                       f"test_questions where survey = '{self.message.survey}')")
        self.expectFalse(cursor.fetchall()[0][0])

    @mock.patch('engine.process.Survey.get_survey')
    def test_get_question(self, get_survey):
        self.num = 14

        get_survey.return_value = self.message.survey

        for i in range(1, 3):
            cursor.execute(f"insert into test_questions (id, survey, author, question) values (default, "
                           f"'{self.message.survey}',{self.message.from_user.id}, 'question{self.num}_{i}')")
            cursor.execute(f"insert into test_features (id, user_id, q_count) values (default, "
                           f"{self.message.from_user.id}, {self.data_get_question})")
        connection.commit()

        self.expectEqual(qa.get_question(self.message), f'question{self.num}_1')

        cursor.execute(f"select q_count from test_features where id = (select max(id) from "
                       f"test_features where user_id = {self.message.from_user.id})")
        self.expectEqual(cursor.fetchall()[0][0], self.result_count)

    def test_get_q_count(self):
        self.num = 15

        cursor.execute(f"insert into test_features (id, user_id, q_count) values (default, "
                       f"{self.message.from_user.id}, {self.data_get_q_count[0]})")
        cursor.execute(f"insert into test_features (id, user_id, q_count) values (default, "
                       f"{self.message.from_user.id}, {self.data_get_q_count[1]})")
        connection.commit()

        self.expectEqual(qa.get_q_count(self.message), self.result_get_q_count)

    def test_set_ans_check(self):
        self.num = 16

        cursor.execute(f"insert into test_features (id, user_id, ans_check) values (default, "
                       f"{self.message.from_user.id}, {self.data_set_ans_check})")
        cursor.execute(f"insert into test_features (id, user_id) values (default, {self.message.from_user.id})")
        connection.commit()

        qa.set_ans_check(self.message)

        cursor.execute(f"select ans_check from test_features where id = (select max(id) from "
                       f"test_features where user_id = {self.message.from_user.id})")
        self.expectEqual(cursor.fetchall()[0][0], self.result_set_ans_check)

    @mock.patch('engine.process.QuestionAnswer.get_q_count')
    @mock.patch('engine.process.Survey.get_survey')
    def test_answer_insert(self, get_survey, q_count):
        self.num = 17

        q_count.side_effect = self.data_answer_insert[0]
        get_survey.return_value = self.message.survey

        self.text = f"answer{self.num}'"

        cursor.execute(f"insert into test_features (id, user_id, survey) values (default, {self.message.from_user.id}, "
                       f"'{self.message.survey}')")
        for i in range(1, 4):
            cursor.execute(f"insert into test_questions (id, survey, author, question) values (default, "
                           f"'{self.message.survey}',{self.message.from_user.id}, 'question{self.num}_{i}')")
        connection.commit()

        self.expectEqual(qa.answer_insert(self.message, self.data_answer_insert[1][0]),
                         answers['ANS_NEXT_Q'] % f'question{self.num}_{self.result_answer_insert[0][0]}')
        self.expectEqual(qa.answer_insert(self.message, self.data_answer_insert[1][1]),
                         answers['ANS_NEXT_Q'] % f'question{self.num}_{self.result_answer_insert[0][1]}')
        self.expectEqual(qa.answer_insert(self.message, self.data_answer_insert[1][2]),
                         answers['ALL_ANSWERED'])

        cursor.execute(f"select answer from test_answers where f_id = "
                       f"(select max(id) from test_features where user_id = {self.message.from_user.id}) order by id")
        self.expectEqual(cursor.fetchall(), self.result_answer_insert[1])

        cursor.execute(f"select q_id from test_answers where f_id = "
                       f"(select max(id) from test_features where user_id = {self.message.from_user.id}) order by id")
        q_id_answers = cursor.fetchall()
        cursor.execute(f"select id from test_questions where survey = '{self.message.survey}' order by id")
        id_questions = cursor.fetchall()

        self.expectEqual(q_id_answers, id_questions)

        self.text = self.text * 40

        self.expectEqual(qa.answer_insert(self.message), answers['LONG'])


class CoordTest(RunAllTestCase, Message, Result):
    """Test Coord class in
       process.py"""
    def test_get_poly_points(self):
        self.num = 18

        cursor.execute(f"insert into test_features (id, user_id, poly_points) values (default, "
                       f"{self.message.from_user.id}, '{self.data_get_pp}')")
        connection.commit()

        self.expectEqual(coord.get_poly_points(self.message), self.result_get_pp)

    @mock.patch('engine.process.Coord.get_poly_points')
    def test_append_poly_points(self, poly_points):
        self.num = 19

        poly_points.side_effect = self.data_append_pp[0]

        lat = self.data_append_pp[1]
        long = self.data_append_pp[2]

        cursor.execute(f"insert into test_features (id, user_id) values (default, {self.message.from_user.id})")
        connection.commit()

        coord.append_poly_points(self.message, lat, long)

        cursor.execute(f"select poly_points from test_features where id = (select max(id) from test_features where "
                       f"user_id = {self.message.from_user.id})")
        self.expectEqual(cursor.fetchall()[0][0], self.result_append_pp[0])

        coord.append_poly_points(self.message, lat, long)

        cursor.execute(f"select poly_points from test_features where id = (select max(id) from test_features where "
                       f"user_id = {self.message.from_user.id})")
        self.expectEqual(cursor.fetchall()[0][0], self.result_append_pp[1])

    @mock.patch('engine.process.Coord.get_poly_points')
    def test_get_count(self, poly_points):
        poly_points.side_effect = self.data_get_count

        self.expectEqual(coord.get_count(self.message), self.result_get_count[0])
        self.expectEqual(coord.get_count(self.message), self.result_get_count[1])

    def test_point_manual(self):
        self.num = 20

        data = self.data_point_polygon_manual
        lat, long = int(data[2][:3]), int(data[2][-3:])
        time = self.data_time

        cursor.execute(f"insert into test_features (id, user_id) values (default, {self.message.from_user.id})")
        connection.commit()

        for i in range(len(data)):
            self.text = data[i]
            if i in [0, 1]:
                self.expectEqual(coord.point_manual(self.message), answers['FOLLOW_TEMPLATE'])
            elif i == 2:
                self.expectEqual(coord.point_manual(self.message), answers['POINT_MEDIA'] % (lat, long))

                cursor.execute(
                    f"select ST_AsText(point), to_char(entr_time, 'YYYY') from test_features where id = "
                    f"(select max(id) from test_features where user_id = {self.message.from_user.id})")
                self.expectEqual(cursor.fetchall()[0], (f'POINT({long} {lat})', time))
            elif i == 3:
                self.expectEqual(coord.point_manual(self.message), answers['INVALID_COORD'])
            elif i == 4:
                self.expectEqual(coord.point_manual(self.message), answers['INVALID_LAT'])
            elif i == 5:
                self.expectEqual(coord.point_manual(self.message), answers['INVALID_LONG'])
            else:
                self.expectEqual(coord.point_manual(self.message), answers['LONG'])

    def test_point_location(self):
        self.num = 21

        cursor.execute(f"insert into test_features (id, user_id) values (default, {self.message.from_user.id})")
        connection.commit()

        self.expectEqual(coord.point_location(self.message), answers['POINT_MEDIA'] % (self.message.location.latitude,
                                                                                       self.message.location.longitude))

        cursor.execute(f"select ST_AsText(point), to_char(entr_time, 'YYYY') from test_features where id = "
                       f"(select max(id) from test_features where user_id = {self.message.from_user.id})")
        self.expectEqual(cursor.fetchall()[0], self.result_point_manual)

    @mock.patch('engine.process.Coord.append_poly_points')
    def test_polygon_manual(self, poly_points):
        self.num = 22

        poly_points.return_value = True

        data = self.data_point_polygon_manual

        for i in range(len(data)):
            self.text = data[i]
            if i in [0, 1]:
                self.expectEqual(coord.polygon_manual(self.message), answers['FOLLOW_TEMPLATE'])
            elif i == 2:
                self.expectEqual(coord.polygon_manual(self.message), answers['VERTEX_DONE'])
            elif i == 3:
                self.expectEqual(coord.polygon_manual(self.message), answers['INVALID_COORD'])
            elif i == 4:
                self.expectEqual(coord.polygon_manual(self.message), answers['INVALID_LAT'])
            elif i == 5:
                self.expectEqual(coord.polygon_manual(self.message), answers['INVALID_LONG'])
            else:
                self.expectEqual(coord.polygon_manual(self.message), answers['LONG'])

    @mock.patch('engine.process.Coord.append_poly_points')
    def test_polygon_location(self, poly_points):
        self.num = 23

        poly_points.return_value = True

        self.expectEqual(coord.polygon_location(self.message), answers['VERTEX_DONE'])

    def test_polygon_create(self):
        self.num = 24

        cursor.execute(f"insert into test_features (id, user_id) values (default, {self.message.from_user.id})")
        connection.commit()

        self.expectEqual(coord.polygon_create(self.message, self.data_polygon_create.split(',')),
                         answers['POLYGON_MEDIA'])

        cursor.execute(f"select ST_AsText(polygon), to_char(entr_time, 'YYYY') from test_features where id = "
                       f"(select max(id) from test_features where user_id = {self.message.from_user.id})")
        self.expectEqual(cursor.fetchall()[0], self.result_polygon_create)


class MediaTest(RunAllTestCase, Message, Result):
    """Test Media class in
       process.py"""
    mock_s3 = mock_s3()

    @mock.patch('datetime.datetime')
    @mock.patch('crc32c.crc32c')
    def test_media_name(self, crc32, now):
        now.return_value = self.data_time
        crc32.return_value = self.data_media_name[0]

        self.expectEqual(media.media_name(self.message, self.data_media_name[1]), self.result_media_name)

    def test_s3_upload(self):
        self.mock_s3.start()

        boto3.resource("s3").Bucket(self.data_s3_upload[0]).create()

        media.s3_upload(self.data_s3_upload[1], self.data_s3_upload[0], self.data_s3_upload[2],
                        self.data_s3_upload[3])

        object_s3 = boto3.resource("s3").Object(self.data_s3_upload[0], self.data_s3_upload[2])
        self.expectEqual(object_s3.get()["Body"].read(), self.result_s3_upload)

        self.expectTrue(media.s3_upload(self.data_s3_upload[1], self.data_s3_upload[0], self.data_s3_upload[2],
                                        self.data_s3_upload[3]))

        self.expectIsNone(media.s3_upload(self.data_s3_upload[1], self.data_s3_upload[4], self.data_s3_upload[2],
                                          self.data_s3_upload[3]))

        self.mock_s3.stop()

    @mock.patch('urllib.request.urlopen')
    @mock.patch('engine.process.Media.media_name')
    @mock.patch('engine.process.Media.s3_upload')
    def test_media_path(self, s3_upload, media_name, urlopen):
        mocked = mock.MagicMock()
        mocked.__enter__.return_value = mocked

        urlopen.return_value = mocked
        media_name.return_value = self.result_media_name
        s3_upload.side_effect = self.data_media_path[3]

        mocked.getcode.return_value = 200
        self.expectEqual(media.media_path(self.data_media_path[0], self.data_media_path[1],
                                          self.message, self.data_media_path[2]), self.result_media_name)
        self.expectIsNone(media.media_path(self.data_media_path[0], self.data_media_path[1],
                                           self.message, self.data_media_path[2]))

        mocked.getcode.return_value = 404
        self.expectIsNone(media.media_path(self.data_media_path[0], self.data_media_path[1],
                                           self.message, self.data_media_path[2]))

    def test_save_media(self):
        self.num = 25

        path = self.result_media_name

        cursor.execute(f"insert into test_features (id, user_id) values (default, {self.message.from_user.id})")
        connection.commit()

        self.expectEqual(media.save_media(self.message, path, 'photo'), answers['MEDIA_SAVED'] % ('photo', 'photo',
                                                                                                  'video'))

        cursor.execute(f"select photo from test_features where id = (select max(id) from test_features where "
                       f"user_id = {self.message.from_user.id})")
        self.expectEqual(cursor.fetchall()[0][0], self.result_save_media)

        self.expectEqual(media.save_media(self.message, path, 'video'), answers['MEDIA_SAVED'] % ('video', 'video',
                                                                                                  'photo'))

        cursor.execute(f"select video from test_features where id = (select max(id) from test_features where "
                       f"user_id = {self.message.from_user.id})")
        self.expectEqual(cursor.fetchall()[0][0], self.result_save_media)

        self.expectEqual(media.save_media(self.message, None, 'photo'), answers['MEDIA_NS'] % ('photo', 'photo',
                                                                                               'video'))
        self.expectEqual(media.save_media(self.message, None, 'video'), answers['MEDIA_NS'] % ('video', 'video',
                                                                                               'photo'))


class CreateWebMapTest(RunAllTestCase, SetTestData, Result):
    """Test CreateWebMap in
       process.py"""
    @mock.patch('engine.process.PointPolygon.polygon')
    @mock.patch('engine.process.PointPolygon.point')
    @mock.patch('engine.process.Survey.get_survey')
    def test_source(self, get_survey, point, polygon):
        self.num = 26

        self.set_test_data()  # set test data

        polygon.side_effect = self.data_double_polygon
        point.side_effect = self.data_double_point
        get_survey.return_value = self.message.survey

        self.expectEqual(webmap.source(f"'{self.message.survey}'"), self.result_source_webmap)

    def test_geom_extent(self):
        self.num = 29

        self.set_test_data()  # set test data

        self.expectEqual(webmap.geom_extent(f"'{self.message.survey}'"), self.result_extent)

    def test_map_center(self):
        self.expectEqual(webmap.map_center(self.data_map_center[0]), self.result_triple_map_center[0])
        self.expectEqual(webmap.map_center(self.data_map_center[1]), self.result_triple_map_center[1])
        self.expectEqual(webmap.map_center(self.data_map_center[2]), self.result_triple_map_center[2])

    @mock.patch('engine.process.CreateWebMap.map_center')
    @mock.patch('engine.process.Survey.get_survey')
    def test_adjust(self, get_survey, map_center):
        self.num = 32

        self.set_test_data()  # set test data

        map_center.side_effect = self.data_triple_map_center
        get_survey.return_value = self.message.survey

        self.expectEqual(webmap.adjust(f"'{self.message.survey}'", self.data_adjust[0], self.data_adjust[1]),
                         self.result_triple_map_center[0])
        self.expectEqual(webmap.adjust(f"'{self.message.survey}'", self.data_adjust[0], None),
                         self.result_triple_map_center[1])
        self.expectEqual(webmap.adjust(f"'{self.message.survey}'", None, self.data_adjust[1]),
                         self.result_triple_map_center[2])

    def test_distance(self):
        adjust = self.data_triple_map_center

        for i in range(len(adjust)):
            self.expectEqual(webmap.distance(adjust[i]), self.result_distance[i])

    def test_get_scale(self):
        distance = self.data_get_scale

        for i in range(len(distance)):
            self.expectEqual(webmap.get_scale(distance[i]), self.result_get_scale[i])

    @mock.patch('engine.process.CreateWebMap.get_scale')
    @mock.patch('engine.process.CreateWebMap.source')
    @mock.patch('engine.process.CreateWebMap.distance')
    @mock.patch('engine.process.CreateWebMap.adjust')
    @mock.patch('engine.process.CreateWebMap.geom_extent')
    @mock.patch('engine.process.Survey.get_survey')
    def test_create(self, get_survey, geom_extent, adjust, distance, source, get_scale):
        self.num = 35

        get_scale.return_value = self.data_scale
        source.return_value = self.data_webmap
        distance.return_value = self.data_distance
        adjust.return_value = self.data_triple_map_center[0]
        geom_extent.return_value = self.data_extent
        get_survey.return_value = self.message.survey

        self.expectEqual(webmap.create(self.message).getvalue(), self.result_webmap)


class CreateGJsonShpTest(RunAllTestCase, SetTestData, Result):
    """Test CreateGJsonShp class in
       process.py"""
    @mock.patch('engine.process.Survey.get_survey')
    def test_ques_ans(self, get_survey):
        self.num = 38

        self.set_test_data()  # set test data

        get_survey.return_value = self.message.survey

        self.expectEqual(gjson_shp.ques_ans(f"'{self.message.survey}'"), self.result_ques_ans)

    @mock.patch('engine.process.CreateGJsonShp.ques_ans')
    @mock.patch('engine.process.Shp.geom_shp')
    @mock.patch('engine.process.GeoJson.geom_gjson')
    @mock.patch('engine.process.Survey.get_survey')
    def test_create(self, get_survey, geom_gjson, geom_shp, ques_ans):
        self.num = 41

        ques_ans.return_value = {}
        geom_shp.side_effect = self.data_gjson_shp[0]
        geom_gjson.side_effect = self.data_gjson_shp[1]
        get_survey.return_value = self.message.survey

        self.expectEqual(gjson_shp.create(self.message, 'shapefile'), self.result_gjson_shp[0])
        self.expectEqual(gjson_shp.create(self.message, 'geojson'), self.result_gjson_shp[1])


class GeoJsonTest(RunAllTestCase, SetTestData, Result):
    """Test GeoJson class in
       process.py"""
    @mock.patch('engine.process.PointPolygon.polygon')
    @mock.patch('engine.process.PointPolygon.point')
    @mock.patch('engine.process.Survey.get_survey')
    def test_gjson(self, get_survey, point, polygon):
        self.num = 44

        self.set_test_data()  # set test data

        polygon.side_effect = self.data_quad_polygon
        point.side_effect = self.data_quad_point
        get_survey.return_value = self.message.survey

        self.expectEqual(gjson.gjson('point', f"'{self.message.survey}'", self.data_question, self.data_double_answer,
                                     self.data_count), self.result_gjson_point)
        self.expectEqual(gjson.gjson('polygon', f"'{self.message.survey}'", self.data_question, self.data_double_answer,
                                     self.data_count), self.result_gjson_polygon)

    @mock.patch('engine.process.GeoJson.gjson')
    def test_geom_gjson(self, geojson):
        self.num = 47

        geojson.side_effect = [self.data_geom_gjson_point, self.data_geom_gjson_polygon]

        self.expectEqual(gjson.geom_gjson(self.message, 'point', f"'{self.message.survey}'",
                                          self.data_ques_ans).getvalue(), self.result_geom_gjson_point)
        self.expectEqual(gjson.geom_gjson(self.message, 'polygon', f"'{self.message.survey}'",
                                          self.data_ques_ans).getvalue(), self.result_geom_gjson_polygon)


class ShpTest(RunAllTestCase, SetTestData, ShpProcess, Result):
    """Test Shp class in
       process.py"""
    @mock.patch('engine.process.PointPolygon.polygon')
    @mock.patch('engine.process.PointPolygon.point')
    @mock.patch('engine.process.Survey.get_survey')
    def test_shp(self, get_survey, point, polygon):
        self.num = 50

        self.set_test_data()  # set test data

        polygon.side_effect = self.data_quad_polygon
        point.side_effect = self.data_quad_point
        get_survey.return_value = self.message.survey

        output = self.shp_value(shp.shp('point', f"'{self.message.survey}'", self.data_question,
                                        self.data_double_answer, self.data_count))
        self.expectEqual(output, self.result_shp_point)

        output = self.shp_value(shp.shp('polygon', f"'{self.message.survey}'", self.data_question,
                                        self.data_double_answer, self.data_count))
        self.expectEqual(output, self.result_shp_polygon)

    @mock.patch('engine.process.Shp.shp')
    @mock.patch('engine.process.Survey.get_survey')
    def test_geom_shp(self, get_survey, shapefile):
        self.num = 53

        shapefile.side_effect = [self.shp_bytes(self.data_geom_shp_point), self.shp_bytes(self.data_geom_shp_polygon)]
        get_survey.return_value = self.message.survey

        output = shp.geom_shp(self.message, 'point', f"'{self.message.survey}'", self.data_ques_ans)
        for i in range(len(output)):
            output[i] = output[i].getvalue()
        self.expectEqual(output, self.result_geom_shp_point)

        output = shp.geom_shp(self.message, 'polygon', f"'{self.message.survey}'", self.data_ques_ans)
        for i in range(len(output)):
            output[i] = output[i].getvalue()
        self.expectEqual(output, self.result_geom_shp_polygon)


class DeleteTest(RunAllTestCase, Message, Result):
    """Test Delete class in
       process.py"""
    @mock.patch('engine.process.Survey.get_survey')
    def test_del_question(self, get_survey):
        self.num = 54

        get_survey.return_value = self.message.survey

        for i in range(1, 3):
            cursor.execute(f"insert into test_questions(survey, author, question) values('{self.message.survey}', "
                           f"{self.message.from_user.id}, 'question{self.num}_{i}')")
        connection.commit()

        delete.del_question(self.message)

        cursor.execute(f"select * from test_questions where survey = '{self.message.survey}'")
        self.expectFalse(cursor.fetchall())

    def test_check_ans(self):
        self.num = 55

        cursor.execute(f"insert into test_features (id, user_id, ans_check) values (default, "
                       f"{self.message.from_user.id}, {self.data_ans_check[0]})")
        connection.commit()

        self.expectEqual(delete.check_ans(self.message), self.result_ans_check[0])

        cursor.execute(f"update test_features set ans_check = {self.data_ans_check[1]} where id = "
                       f"(select max(id) from test_features where user_id = {self.message.from_user.id})")
        connection.commit()

        self.expectFalse(delete.check_ans(self.message))

    def test_del_row(self):
        self.num = 56

        cursor.execute(f"insert into test_features (id, user_id) values (default, {self.message.from_user.id})")
        cursor.execute(f"insert into test_answers (id, f_id) values (default, (select max(id) from test_features where "
                       f"user_id = {self.message.from_user.id}))")
        connection.commit()

        cursor.execute(f"select max(id) from test_features where user_id = {self.message.from_user.id}")
        f_id = cursor.fetchall()[0][0]

        delete.del_row(self.message)

        cursor.execute(f"select * from test_answers where f_id = {f_id}")
        self.expectFalse(cursor.fetchall())

        cursor.execute(f"select * from test_features where id = {f_id}")
        self.expectFalse(cursor.fetchall())

    @mock.patch('engine.process.Survey.get_survey')
    def test_del_data(self, get_survey):
        self.num = 57

        get_survey.return_value = self.message.survey

        for i in range(3):
            cursor.execute(f"insert into test_features (id, user_id, survey, ans_check) values "
                           f"(default, {self.message.from_user.id}, '{self.message.survey}', {self.data_ans_check[0]})")
            cursor.execute(f"insert into test_answers (id, f_id) values (default, (select max(id) from "
                           f"test_features where user_id = {self.message.from_user.id}))")
        connection.commit()

        cursor.execute(f"select id from test_features where survey = '{self.message.survey}' and "
                       f"ans_check = {self.data_ans_check[0]}")
        id_list = cursor.fetchall()

        delete.del_data(self.message)

        for elem in id_list:
            cursor.execute(f"select * from test_answers where f_id = {elem[0]}")
            self.expectFalse(cursor.fetchall())

        cursor.execute(f"select * from test_features where survey = '{self.message.survey}' and ans_check = "
                       f"{self.data_ans_check[0]}")
        self.expectFalse(cursor.fetchall())

    def test_del_feature(self):
        self.num = 58

        cursor.execute(f"insert into test_features (id, user_id) values (default, {self.message.from_user.id})")
        connection.commit()

        cursor.execute(f"select max(id) from test_features where user_id = {self.message.from_user.id}")
        max_id = cursor.fetchall()[0][0]

        delete.del_feature(self.message)

        cursor.execute(f"select * from test_features where id = {max_id}")
        self.expectFalse(cursor.fetchall())


if __name__ == "__main__":
    main()
