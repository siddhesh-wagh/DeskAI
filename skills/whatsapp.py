from skills.base import BaseSkill
from core.dispatcher import command
from core.context import AssistantContext
import pywhatkit as kit


class WhatsAppManualSkill(BaseSkill):
    def execute(self, context: AssistantContext, query: str, **params):
        try:
            number = input("Enter phone number (10 digits): ").strip()

            if not number.isdigit() or len(number) != 10:
                return self.error_response("Invalid number")

            message = input("Enter your message: ").strip()

            if not message:
                return self.error_response("Message cannot be empty")

            phone = "+91" + number

            kit.sendwhatmsg_instantly(phone, message, wait_time=10, tab_close=True)

            return self.success_response(f"Message sent to {number}")

        except Exception as e:
            return self.error_response(f"Failed: {e}")


@command(["send whatsapp message", "whatsapp"], priority=5)
def cmd_whatsapp_manual(ctx: AssistantContext, query: str):
    return WhatsAppManualSkill().execute(ctx, query)