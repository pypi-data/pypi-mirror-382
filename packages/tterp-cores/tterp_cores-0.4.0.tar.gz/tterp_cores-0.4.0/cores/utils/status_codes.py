class StatusCode:
    """
    Lớp chứa các mã trạng thái HTTP và mô tả của chúng.

    Các mã trạng thái được nhóm theo loại:
    - 1xx: Thông tin
    - 2xx: Thành công
    - 3xx: Chuyển hướng
    - 4xx: Lỗi phía client
    - 5xx: Lỗi phía server
    """

    # 1xx: Thông tin
    CONTINUE = 100
    """
    Phản hồi tạm thời này cho biết mọi thứ cho đến nay đều OK và client nên tiếp tục request
    hoặc bỏ qua nếu đã hoàn thành.
    """

    SWITCHING_PROTOCOLS = 101
    """
    Mã này được gửi để phản hồi cho header Upgrade từ client và cho biết giao thức
    mà server đang chuyển sang.
    """

    PROCESSING = 102
    """
    Mã này cho biết server đã nhận và đang xử lý request, nhưng chưa có phản hồi.
    """

    # 2xx: Thành công
    OK = 200
    """
    Request đã thành công. Ý nghĩa của thành công thay đổi tùy theo phương thức HTTP:
    - GET: Tài nguyên đã được lấy và truyền trong body.
    - HEAD: Các header entity nằm trong body.
    - POST: Tài nguyên mô tả kết quả của hành động được truyền trong body.
    - TRACE: Body chứa thông điệp request như đã nhận bởi server.
    """

    CREATED = 201
    """
    Request đã thành công và một tài nguyên mới đã được tạo. Đây thường là phản hồi được gửi
    sau một request PUT.
    """

    ACCEPTED = 202
    """
    Request đã được nhận nhưng chưa được xử lý. Request có thể hoặc không được xử lý,
    vì có thể bị từ chối sau khi xử lý.
    """

    NON_AUTHORITATIVE_INFORMATION = 203
    """
    Mã phản hồi này có nghĩa là tập meta-information được trả về không phải là tập chính xác
    như có sẵn từ origin server, mà được thu thập từ bản sao cục bộ hoặc bên thứ ba.
    """

    NO_CONTENT = 204
    """
    Không có nội dung để gửi cho request này, nhưng các headers có thể hữu ích.
    User-agent có thể cập nhật các headers được cache cho tài nguyên này.
    """

    RESET_CONTENT = 205
    """
    Mã phản hồi này được gửi sau khi hoàn thành request để yêu cầu user agent
    reset document view đã gửi request này.
    """

    PARTIAL_CONTENT = 206
    """
    Mã phản hồi này được sử dụng vì header range được gửi từ client để tách tải xuống
    thành nhiều luồng.
    """

    MULTI_STATUS = 207
    """
    Phản hồi Multi-Status truyền tải thông tin về nhiều tài nguyên trong tình huống
    mà nhiều mã trạng thái có thể phù hợp.
    """

    # 3xx: Chuyển hướng
    MULTIPLE_CHOICES = 300
    """
    Request có nhiều phản hồi có thể xảy ra. User-agent hoặc user nên chọn một trong số chúng.
    Không có cách chuẩn hóa để chọn một trong các phản hồi.
    """

    MOVED_PERMANENTLY = 301
    """
    Mã phản hồi này có nghĩa là URI của tài nguyên được yêu cầu đã thay đổi.
    Có thể, URI mới sẽ được đưa ra trong phản hồi.
    """

    MOVED_TEMPORARILY = 302
    """
    Mã phản hồi này có nghĩa là URI của tài nguyên được yêu cầu đã thay đổi tạm thời.
    Thay đổi mới trong URI có thể được thực hiện trong tương lai. Do đó, URI này nên được
    client sử dụng trong các request tương lai.
    """

    SEE_OTHER = 303
    """
    Server gửi phản hồi này để hướng client lấy tài nguyên được yêu cầu từ URI khác
    với một request GET.
    """

    NOT_MODIFIED = 304
    """
    Điều này được sử dụng cho mục đích caching. Nó cho client biết rằng phản hồi chưa
    được sửa đổi. Vì vậy, client có thể tiếp tục sử dụng phiên bản cache của phản hồi.
    """

    USE_PROXY = 305
    """
    Đã được định nghĩa trong phiên bản trước của đặc tả HTTP để chỉ ra rằng phản hồi được yêu cầu
    phải được truy cập bởi proxy. Nó đã bị phản đối do các mối lo ngại bảo mật liên quan đến
    cấu hình in-band của proxy.
    """

    TEMPORARY_REDIRECT = 307
    """
    Server gửi phản hồi này để hướng client lấy tài nguyên được yêu cầu đến URI khác
    với cùng phương thức đã sử dụng trong request trước đó.
    """

    PERMANENT_REDIRECT = 308
    """
    Điều này có nghĩa là tài nguyên bây giờ được đặt vĩnh viễn tại URI khác, được chỉ định
    bởi header Location trong HTTP Response.
    """

    # 4xx: Lỗi phía client
    BAD_REQUEST = 400
    """
    Phản hồi này có nghĩa là server không thể hiểu request do cú pháp không hợp lệ.
    """

    UNAUTHORIZED = 401
    """
    Mặc dù tiêu chuẩn HTTP quy định là "unauthorized", nhưng ngữ nghĩa phản hồi này là "unauthenticated".
    Đó là, client phải xác thực chính nó để nhận được phản hồi được yêu cầu.
    """

    PAYMENT_REQUIRED = 402
    """
    Mã phản hồi này được dành cho sử dụng trong tương lai.
    """

    FORBIDDEN = 403
    """
    Client không có quyền truy cập vào nội dung, tức là không được phép, nên server đang
    từ chối cung cấp phản hồi thích hợp. Không giống như 401, danh tính của client đã được server biết.
    """

    NOT_FOUND = 404
    """
    Server không thể tìm thấy tài nguyên được yêu cầu. Trong trình duyệt, điều này có nghĩa
    là URL không được công nhận. Trong API, điều này cũng có thể có nghĩa là endpoint hợp lệ
    nhưng chính resource không tồn tại.
    """

    METHOD_NOT_ALLOWED = 405
    """
    Phương thức request được server biết đến nhưng đã bị vô hiệu hóa và không thể sử dụng.
    """

    NOT_ACCEPTABLE = 406
    """
    Phản hồi này được gửi khi web server, sau khi thực hiện server-driven content negotiation,
    không tìm thấy bất kỳ nội dung nào theo tiêu chí do user agent đưa ra.
    """

    PROXY_AUTHENTICATION_REQUIRED = 407
    """
    Điều này tương tự như 401 nhưng xác thực cần được thực hiện bởi proxy.
    """

    REQUEST_TIMEOUT = 408
    """
    Phản hồi này được gửi trên một kết nối idle bởi một số server, ngay cả khi không có
    request trước đó từ client.
    """

    CONFLICT = 409
    """
    Phản hồi này được gửi khi một request xung đột với trạng thái hiện tại của server.
    """

    GONE = 410
    """
    Phản hồi này sẽ được gửi khi nội dung được yêu cầu đã bị xóa vĩnh viễn khỏi server,
    không có địa chỉ chuyển tiếp.
    """

    LENGTH_REQUIRED = 411
    """
    Server từ chối request vì trường header Content-Length không được định nghĩa và
    server yêu cầu nó.
    """

    PRECONDITION_FAILED = 412
    """
    Client đã chỉ ra điều kiện tiên quyết trong các headers của nó mà server không đáp ứng.
    """

    REQUEST_TOO_LONG = 413
    """
    Request entity lớn hơn giới hạn được xác định bởi server.
    """

    REQUEST_URI_TOO_LONG = 414
    """
    URI được yêu cầu bởi client dài hơn server sẵn sàng diễn giải.
    """

    UNSUPPORTED_MEDIA_TYPE = 415
    """
    Định dạng media của dữ liệu được yêu cầu không được server hỗ trợ.
    """

    REQUESTED_RANGE_NOT_SATISFIABLE = 416
    """
    Phạm vi được chỉ định bởi trường header Range trong request không thể được thực hiện.
    """

    EXPECTATION_FAILED = 417
    """
    Mã phản hồi này có nghĩa là kỳ vọng được chỉ ra bởi trường header Expect
    của request không thể được đáp ứng bởi server.
    """

    IM_A_TEAPOT = 418
    """
    Bất kỳ nỗ lực nào để pha cà phê với một ấm trà đều dẫn đến mã lỗi "418 I'm a teapot".
    """

    INSUFFICIENT_SPACE_ON_RESOURCE = 419
    """
    Mã trạng thái 507 (Insufficient Storage) có nghĩa là phương thức không thể được thực hiện
    trên tài nguyên vì server không thể lưu trữ đại diện cần thiết để hoàn thành request thành công.
    """

    METHOD_FAILURE = 420
    """
    Một phản hồi không dùng nữa được sử dụng bởi Spring Framework khi một phương thức đã thất bại.
    """

    MISDIRECTED_REQUEST = 421
    """
    Được định nghĩa trong đặc tả của HTTP/2 để chỉ ra rằng server không thể tạo phản hồi
    cho sự kết hợp của scheme và authority được bao gồm trong URI request.
    """

    UNPROCESSABLE_ENTITY = 422
    """
    Request được định dạng tốt nhưng không thể được tuân theo do lỗi ngữ nghĩa.
    """

    LOCKED = 423
    """
    Tài nguyên đang được truy cập bị khóa.
    """

    FAILED_DEPENDENCY = 424
    """
    Request thất bại do thất bại của request trước đó.
    """

    PRECONDITION_REQUIRED = 428
    """
    Origin server yêu cầu request phải có điều kiện.
    """

    TOO_MANY_REQUESTS = 429
    """
    Người dùng đã gửi quá nhiều request trong một khoảng thời gian nhất định.
    """

    REQUEST_HEADER_FIELDS_TOO_LARGE = 431
    """
    Server không sẵn lòng xử lý request vì các trường header của nó quá lớn.
    """

    UNAVAILABLE_FOR_LEGAL_REASONS = 451
    """
    Người dùng đã yêu cầu tài nguyên bất hợp pháp, chẳng hạn như trang web bị chính phủ kiểm duyệt.
    """

    # 5xx: Lỗi phía server
    INTERNAL_SERVER_ERROR = 500
    """
    Server gặp phải một tình huống không mong đợi khiến nó không thể thực hiện request.
    """

    NOT_IMPLEMENTED = 501
    """
    Phương thức request không được hỗ trợ bởi server và không thể xử lý.
    """

    BAD_GATEWAY = 502
    """
    Phản hồi lỗi này có nghĩa là server, trong khi làm việc như một gateway để lấy phản hồi
    cần thiết để xử lý request, đã nhận được phản hồi không hợp lệ.
    """

    SERVICE_UNAVAILABLE = 503
    """
    Server không sẵn sàng xử lý request. Nguyên nhân phổ biến là server bị mất do bảo trì
    hoặc quá tải.
    """

    GATEWAY_TIMEOUT = 504
    """
    Phản hồi lỗi này được đưa ra khi server đang hoạt động như một gateway và không thể
    nhận được phản hồi kịp thời.
    """

    HTTP_VERSION_NOT_SUPPORTED = 505
    """
    Phiên bản HTTP được sử dụng trong request không được server hỗ trợ.
    """

    VARIANT_ALSO_NEGOTIATES = 506
    """
    Server có lỗi cấu hình nội bộ: variant resource được cấu hình để tham gia vào
    transparent content negotiation và là một endpoint không phù hợp trong quá trình negotiation.
    """

    INSUFFICIENT_STORAGE = 507
    """
    Server không thể lưu trữ đại diện cần thiết để hoàn thành request.
    """

    LOOP_DETECTED = 508
    """
    Server phát hiện ra một vòng lặp vô hạn trong khi xử lý request.
    """

    NOT_EXTENDED = 510
    """
    Cần có thêm extensions cho server xử lý request.
    """

    NETWORK_AUTHENTICATION_REQUIRED = 511
    """
    Mã trạng thái 511 cho biết rằng client cần xác thực để có quyền truy cập mạng.
    """
