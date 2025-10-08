from marshmallow import Schema, EXCLUDE, fields

class ExecutableJobConfigSchema(Schema):
    queue = fields.String(
        required=True,
        description="Name of queue on which to place task.",
        example="my-default-queue",
    )
    task = fields.String(
        required=True,
        description="Path to task to invoke.",
        example="my_app.module.method",
    )

class ExecutableJobSchema(Schema):
    """Definition of a single schedule entry"""
    class Meta:
        unknown = EXCLUDE

    name = fields.String(
        required=True,
        description="Name of schedule entry.",
        example="My Scheduled Task",
    )
    schemaVersion = fields.Integer(required=True)
    config = fields.Dict(required=True)
    enabled = fields.Boolean(
        required=True, description="Whether entry is enabled.", example=True
    )
    config = fields.Nested(
        ExecutableJobConfigSchema,
        required=True,
        description="Configuration information for this job.",
    )

