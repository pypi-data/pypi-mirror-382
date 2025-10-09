
import rubigram


class ReportObject:
    async def report_object(
            self: "rubigram.Client",
            object_guid: str,
            report_type: "rubigram.enums.ReportType",
            description: str = None,
            message_id: str = None,
            report_type_object: "rubigram.enums.ReportTypeObject" = 'Object',
    ) -> rubigram.types.Update:
        """
        Report an object (user, channel, group, etc.) for a specific reason.

        Args:
            object_guid (str): The identifier of the object to be reported.
            report_type (rubigram.enums.ReportType): The type of report.
            description (str, optional): Additional description for the report.
            report_type_object (str, optional): The type of object being reported.

        Returns:
            rubigram.types.Update: The update containing information about the report.
        """
        input = dict(
            object_guid=object_guid,
            report_description=description,
            report_type=report_type,
            report_type_object=report_type_object,
        )

        if message_id is not None:
            input['message_id'] = message_id

        return await self.builder(
            name='reportObject',
            input=input,
        )
