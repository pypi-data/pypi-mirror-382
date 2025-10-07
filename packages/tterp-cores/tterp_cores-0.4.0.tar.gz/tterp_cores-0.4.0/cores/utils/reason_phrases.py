class ReasonPhrase:
    """
    Lớp này chứa các mô tả cho các mã trạng thái HTTP.
    Tài liệu chính thức: https://tools.ietf.org/html/rfc7231#section-6
    """

    ACCEPTED = "Accepted"
    """
    Yêu cầu đã được nhận nhưng chưa được xử lý.
    Điều này không ràng buộc, nghĩa là không có cách nào trong HTTP để gửi phản hồi không đồng bộ sau này chỉ ra kết quả xử lý yêu cầu.
    Nó được sử dụng cho các trường hợp khi một quá trình hoặc server khác xử lý yêu cầu, hoặc cho xử lý hàng loạt.
    """

    BAD_GATEWAY = "Bad Gateway"
    """
    Phản hồi lỗi này nghĩa là server, trong khi làm việc như một gateway để nhận phản hồi cần thiết để xử lý yêu cầu, đã nhận được phản hồi không hợp lệ.
    """

    BAD_REQUEST = "Bad Request"
    """
    Phản hồi này nghĩa là server không thể hiểu được yêu cầu do cú pháp không hợp lệ.
    """

    CONFLICT = "Conflict"
    """
    Phản hồi này được gửi khi một yêu cầu xung đột với trạng thái hiện tại của server.
    """

    CONTINUE = "Continue"
    """
    Phản hồi tạm thời này chỉ ra rằng mọi thứ đến nay đều OK và client nên tiếp tục yêu cầu hoặc bỏ qua nếu đã hoàn thành.
    """

    CREATED = "Created"
    """
    Yêu cầu đã thành công và một tài nguyên mới đã được tạo ra. Đây thường là phản hồi được gửi sau một yêu cầu PUT.
    """

    EXPECTATION_FAILED = "Expectation Failed"
    """
    Mã phản hồi này nghĩa là kỳ vọng được chỉ ra bởi trường header Expect của yêu cầu không thể được đáp ứng bởi server.
    """

    FAILED_DEPENDENCY = "Failed Dependency"
    """
    Yêu cầu thất bại do thất bại của một yêu cầu trước đó.
    """

    FORBIDDEN = "Forbidden"
    """
    Client không có quyền truy cập vào nội dung, nghĩa là họ không được ủy quyền, nên server từ chối cung cấp phản hồi phù hợp. Khác với 401, danh tính của client được server biết đến.
    """

    GATEWAY_TIMEOUT = "Gateway Timeout"
    """
    Phản hồi lỗi này được đưa ra khi server đang hoạt động như một gateway và không thể nhận được phản hồi kịp thời.
    """

    GONE = "Gone"
    """
    Phản hồi này được gửi khi nội dung được yêu cầu đã bị xóa vĩnh viễn khỏi server, không có địa chỉ chuyển tiếp.
    Client được mong đợi sẽ xóa cache và liên kết đến tài nguyên.
    """

    HTTP_VERSION_NOT_SUPPORTED = "HTTP Version Not Supported"
    """
    Phiên bản HTTP được sử dụng trong yêu cầu không được server hỗ trợ.
    """

    IM_A_TEAPOT = "I'm a teapot"
    """
    Mọi nỗ lực pha cà phê với một ấm trà sẽ dẫn đến mã lỗi "418 I'm a teapot". Thực thể kết quả có thể ngắn và mập.
    """

    INSUFFICIENT_SPACE_ON_RESOURCE = "Insufficient Space on Resource"
    """
    Mã trạng thái 507 (Insufficient Storage) nghĩa là phương thức không thể được thực hiện trên tài nguyên vì server không thể lưu trữ đại diện cần thiết để hoàn thành yêu cầu thành công.
    """

    INSUFFICIENT_STORAGE = "Insufficient Storage"
    """
    Server có lỗi cấu hình nội bộ: variant resource được cấu hình để tham gia vào transparent content negotiation và là một endpoint không phù hợp trong quá trình negotiation.
    """

    INTERNAL_SERVER_ERROR = "Internal Server Error"
    """
    Server gặp phải một tình huống không mong đợi khiến nó không thể thực hiện yêu cầu.
    """

    LENGTH_REQUIRED = "Length Required"
    """
    Server từ chối yêu cầu vì trường header Content-Length không được định nghĩa và server yêu cầu nó.
    """

    LOCKED = "Locked"
    """
    Tài nguyên đang được truy cập bị khóa.
    """

    METHOD_FAILURE = "Method Failure"
    """
    Một phản hồi không còn được sử dụng bởi Spring Framework khi một phương thức đã thất bại.
    """

    METHOD_NOT_ALLOWED = "Method Not Allowed"
    """
    Phương thức yêu cầu được server biết đến nhưng đã bị vô hiệu hóa và không thể sử dụng.
    """

    MOVED_PERMANENTLY = "Moved Permanently"
    """
    Mã phản hồi này nghĩa là URI của tài nguyên được yêu cầu đã thay đổi. Có thể, URI mới sẽ được đưa ra trong phản hồi.
    """

    MOVED_TEMPORARILY = "Moved Temporarily"
    """
    Mã phản hồi này nghĩa là URI của tài nguyên được yêu cầu đã thay đổi tạm thời.
    """

    MULTI_STATUS = "Multi-Status"
    """
    Phản hồi Multi-Status truyền tải thông tin về nhiều tài nguyên trong tình huống mà nhiều mã trạng thái có thể phù hợp.
    """

    MULTIPLE_CHOICES = "Multiple Choices"
    """
    Yêu cầu có nhiều phản hồi có thể xảy ra. User-agent hoặc user nên chọn một trong số chúng. Không có cách chuẩn hóa để chọn một trong các phản hồi.
    """

    NETWORK_AUTHENTICATION_REQUIRED = "Network Authentication Required"
    """
    Mã trạng thái 511 chỉ ra rằng client cần xác thực để có quyền truy cập mạng.
    """

    NO_CONTENT = "No Content"
    """
    Không có nội dung để gửi cho yêu cầu này, nhưng các headers có thể hữu ích.
    """

    NON_AUTHORITATIVE_INFORMATION = "Non Authoritative Information"
    """
    Mã phản hồi này nghĩa là tập meta-information được trả về không phải là tập chính xác như có sẵn từ origin server, mà được thu thập từ bản sao cục bộ hoặc bên thứ ba.
    """

    NOT_ACCEPTABLE = "Not Acceptable"
    """
    Phản hồi này được gửi khi web server, sau khi thực hiện server-driven content negotiation, không tìm thấy bất kỳ nội dung nào theo tiêu chí do user agent đưa ra.
    """

    NOT_FOUND = "Not Found"
    """
    Server không thể tìm thấy tài nguyên được yêu cầu. Trong trình duyệt, điều này có nghĩa là URL không được công nhận.
    """

    NOT_IMPLEMENTED = "Not Implemented"
    """
    Phương thức yêu cầu không được hỗ trợ bởi server và không thể xử lý.
    """

    NOT_MODIFIED = "Not Modified"
    """
    Điều này được sử dụng cho mục đích caching. Nó cho client biết rằng phản hồi chưa được sửa đổi.
    """

    OK = "OK"
    """
    Yêu cầu đã thành công. Ý nghĩa của thành công thay đổi tùy theo phương thức HTTP.
    """

    PARTIAL_CONTENT = "Partial Content"
    """
    Mã phản hồi này được sử dụng do header range được gửi bởi client để tách tải xuống thành nhiều luồng.
    """

    PAYMENT_REQUIRED = "Payment Required"
    """
    Mã phản hồi này được dành cho sử dụng trong tương lai.
    """

    PERMANENT_REDIRECT = "Permanent Redirect"
    """
    Điều này có nghĩa là tài nguyên bây giờ được đặt vĩnh viễn tại URI khác.
    """

    PRECONDITION_FAILED = "Precondition Failed"
    """
    Client đã chỉ ra điều kiện tiên quyết trong các headers của nó mà server không đáp ứng.
    """

    PRECONDITION_REQUIRED = "Precondition Required"
    """
    Origin server yêu cầu yêu cầu phải có điều kiện.
    """

    PROCESSING = "Processing"
    """
    Mã này chỉ ra rằng server đã nhận và đang xử lý yêu cầu, nhưng chưa có phản hồi.
    """

    PROXY_AUTHENTICATION_REQUIRED = "Proxy Authentication Required"
    """
    Điều này tương tự như 401 nhưng xác thực cần được thực hiện bởi proxy.
    """

    REQUEST_HEADER_FIELDS_TOO_LARGE = "Request Header Fields Too Large"
    """
    Server không sẵn lòng xử lý yêu cầu vì các trường header của nó quá lớn.
    """

    REQUEST_TIMEOUT = "Request Timeout"
    """
    Phản hồi này được gửi trên một kết nối idle bởi một số server, ngay cả khi không có yêu cầu trước đó từ client.
    """

    REQUEST_TOO_LONG = "Request Entity Too Large"
    """
    Request entity lớn hơn giới hạn được xác định bởi server.
    """

    REQUEST_URI_TOO_LONG = "Request-URI Too Long"
    """
    URI được yêu cầu bởi client dài hơn server sẵn sàng diễn giải.
    """

    REQUESTED_RANGE_NOT_SATISFIABLE = "Requested Range Not Satisfiable"
    """
    Phạm vi được chỉ định bởi trường header Range trong yêu cầu không thể được thực hiện.
    """

    RESET_CONTENT = "Reset Content"
    """
    Mã phản hồi này được gửi sau khi hoàn thành yêu cầu để yêu cầu user agent reset document view đã gửi yêu cầu này.
    """

    SEE_OTHER = "See Other"
    """
    Server gửi phản hồi này để hướng client lấy tài nguyên được yêu cầu đến URI khác với một yêu cầu GET.
    """

    SERVICE_UNAVAILABLE = "Service Unavailable"
    """
    Server không sẵn sàng xử lý yêu cầu. Nguyên nhân phổ biến là server bị mất do bảo trì hoặc quá tải.
    """

    SWITCHING_PROTOCOLS = "Switching Protocols"
    """
    Mã này được gửi để phản hồi cho header Upgrade từ client và cho biết giao thức mà server đang chuyển sang.
    """

    TEMPORARY_REDIRECT = "Temporary Redirect"
    """
    Yêu cầu nên được lặp lại với URI khác; tuy nhiên, các yêu cầu trong tương lai vẫn nên sử dụng URI ban đầu.
    """

    TOO_MANY_REQUESTS = "Too Many Requests"
    """
    Người dùng đã gửi quá nhiều yêu cầu trong một khoảng thời gian nhất định.
    """

    UNAUTHORIZED = "Unauthorized"
    """
    Client phải xác thực để nhận được phản hồi được yêu cầu.
    """

    UNPROCESSABLE_ENTITY = "Unprocessable Entity"
    """
    Server hiểu loại nội dung của yêu cầu, và cú pháp của yêu cầu là chính xác, nhưng không thể xử lý các hướng dẫn chứa trong đó.
    """

    UNSUPPORTED_MEDIA_TYPE = "Unsupported Media Type"
    """
    Định dạng media của dữ liệu được yêu cầu không được server hỗ trợ.
    """

    UPGRADE_REQUIRED = "Upgrade Required"
    """
    Server từ chối thực hiện yêu cầu sử dụng giao thức hiện tại nhưng có thể sẵn sàng làm như vậy sau khi client nâng cấp lên giao thức khác.
    """

    VARIANT_ALSO_NEGOTIATES = "Variant Also Negotiates"
    """
    Server có lỗi cấu hình nội bộ: variant resource được cấu hình để tham gia vào transparent content negotiation và là một endpoint không phù hợp trong quá trình negotiation.
    """

    def __init__(self):
        raise NotImplementedError(
            "This class is a collection of constants and should not be instantiated."
        )
