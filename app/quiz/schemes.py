from marshmallow import Schema, fields, validate


class ThemeSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )


class AnswerSchema(Schema):
    title = fields.Str(
        required=True,
    )
    is_correct = fields.Bool(required=True)


class QuestionSchema(Schema):
    theme_id = fields.Int(required=True)
    title = fields.Str(
        required=True,
        validate=validate.Length(min=5, max=200)
    )
    answers = fields.List(
        fields.Nested(AnswerSchema),
        required=True,
        validate=validate.Length(min=2) 
    )


class ThemeResponseSchema(Schema):
    id = fields.Int(required=True)
    title = fields.Str(required=True)


class ThemeListResponseSchema(Schema):
    themes = fields.List(
        fields.Nested(ThemeResponseSchema),
        required=True
    )


class QuestionResponseSchema(Schema):
    id = fields.Int(required=True)
    title = fields.Str(required=True)
    theme_id = fields.Int(required=True)
    answers = fields.List(
        fields.Nested(AnswerSchema),
        required=True
    )


class QuestionListResponseSchema(Schema):
    questions = fields.List(
        fields.Nested(QuestionResponseSchema),
        required=True
    )


class ThemeIdSchema(Schema):
    theme_id = fields.Int(required=True)