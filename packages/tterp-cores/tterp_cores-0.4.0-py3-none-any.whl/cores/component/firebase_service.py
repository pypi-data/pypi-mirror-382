
import firebase_admin
from firebase_admin import credentials, messaging


class FirebaseService:
    def __init__(self, cred_path: str):
        # Kiểm tra nếu Firebase app chưa được khởi tạo
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("[FirebaseService] Firebase Admin SDK initialized")
        else:
            print("[FirebaseService] Firebase Admin SDK already initialized")

    def send_notification(self, token: str, title: str, body: str) -> str:
        # Tạo thông báo
        # print(f"body: {body}")
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
            ),
            token=token,
            data={
                "title": title,
                "body": body,
            },
        )
        # message = messaging.Message(
        #     data={  # Chỉ gửi payload dữ liệu mà không có thông báo
        #             "title": title,
        #             "body": body,
        #     },
        #     token=token
        # )
        # Gửi thông báo và trả về ID của thông báo
        response = messaging.send(message)
        return response

    def send_notification_to_tokens(
        self,
        tokens: list[str],
        title: str,
        body: str,
        data: dict | None = None
    ) -> dict:
        """
        Gửi notification tới nhiều tokens sử dụng MulticastMessage
        """
        try:
            # Validate inputs
            if not tokens:
                print("[FirebaseService] No tokens provided")
                return {"success_count": 0, "failure_count": 0}

            if len(tokens) > 500:
                warning_msg = (f"[FirebaseService] Warning: Token count "
                               f"({len(tokens)}) exceeds limit of 500")
                print(warning_msg)
                tokens = tokens[:500]

            print(f"[FirebaseService] Sending to {len(tokens)} tokens")
            print(f"[FirebaseService] Title: {title}")
            print(f"[FirebaseService] Body length: {len(body)} chars")
            # Validate data dictionary
            if data:
                # Convert all data values to strings (FCM requirement)
                validated_data = {str(k): str(v) for k, v in data.items()}
            else:
                validated_data = {}

            print(f"[FirebaseService] Data payload: {validated_data}")

            # Tạo MulticastMessage với API mới
            message = messaging.MulticastMessage(
                tokens=tokens,
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=validated_data
            )

            # Gửi message sử dụng API mới
            response = messaging.send_each_for_multicast(message)

            success_msg = (f"[FirebaseService] Send result: "
                           f"{response.success_count} success, "
                           f"{response.failure_count} failures")
            print(success_msg)

            # Log chi tiết lỗi nếu có
            if response.failure_count > 0:
                failed_details = []
                for idx, resp in enumerate(response.responses):
                    if not resp.success:
                        error_msg = (str(resp.exception) if resp.exception
                                     else "Unknown error")
                        failed_details.append({
                            'token_index': idx,
                            'error': error_msg
                        })
                print(f"[FirebaseService] Failed count: {len(failed_details)}")

            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "responses": response.responses
            }

        except Exception as e:
            error_msg = f"[FirebaseService] Error in send_notification: {e}"
            print(error_msg)
            print(f"[FirebaseService] Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise e
