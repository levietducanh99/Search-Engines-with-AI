# Báo Cáo Về Thư Mục `models`

## Tổng Quan
Thư mục `models` trong dự án được sử dụng để định nghĩa các kiểu dữ liệu trả về của từng loại tìm kiếm. Các kiểu dữ liệu này được xây dựng bằng cách sử dụng thư viện `pydantic`, giúp đảm bảo tính chính xác và dễ dàng kiểm tra dữ liệu.

## Các Thành Phần Chính

### Base Models
- **BaseSearchResult**: Là model cơ sở cho tất cả các kết quả tìm kiếm. Nó bao gồm các trường cơ bản như `id`, `title`, và `content`.

### Keyword Search Models
- **KeywordSearchResult**: Định nghĩa kết quả tìm kiếm từ khóa, bao gồm các trường như `bm25_score`, `keywords`, và `matched_count`.
- **KeywordSearchResponse**: Định nghĩa phản hồi cho tìm kiếm từ khóa, bao gồm danh sách kết quả và thông tin tổng quan như `total` và `processing_time_ms`.

### Semantic Search Models
- **SemanticSearchResult**: Định nghĩa kết quả tìm kiếm ngữ nghĩa, với các trường như `semantic_score`, `semantic_context`, và `matched_count`.
- **SemanticSearchResponse**: Định nghĩa phản hồi cho tìm kiếm ngữ nghĩa, bao gồm danh sách kết quả và thông tin tổng quan như `total` và `processing_time_ms`.

### Combined Search Models
- **CombinedSearchResult**: Định nghĩa kết quả tìm kiếm kết hợp, bao gồm các trường như `bm25_score`, `semantic_score`, `rrf_score`, và `ranking`.
- **UnifiedSearchResponse**: Định nghĩa phản hồi tìm kiếm thống nhất, bao gồm danh sách kết quả từ khóa, ngữ nghĩa, và kết hợp, cùng với thông tin phân trang và thời gian xử lý.

### Request Models
- **SearchRequest**: Định nghĩa yêu cầu tìm kiếm, bao gồm các trường như `query`, `page`, và `page_size`. Model này đảm bảo rằng truy vấn tìm kiếm không được để trống.

## Vai Trò
Thư mục `models` đóng vai trò quan trọng trong việc chuẩn hóa dữ liệu giữa các thành phần của hệ thống. Nó giúp:
1. **Đảm bảo Tính Chính Xác**: Các kiểu dữ liệu được định nghĩa rõ ràng, giúp giảm thiểu lỗi trong quá trình xử lý.
2. **Dễ Dàng Bảo Trì**: Các model được tổ chức tốt, giúp việc mở rộng và bảo trì trở nên dễ dàng.
3. **Tích Hợp Hiệu Quả**: Các model này được sử dụng trong cả back-end và front-end để đảm bảo tính nhất quán.

---

**Người viết báo cáo:** GitHub Copilot

# Báo Cáo Về Thư Mục `services`

## Tổng Quan
Thư mục `services` trong dự án được sử dụng để triển khai các logic nghiệp vụ và xử lý các yêu cầu phức tạp từ hệ thống. Đây là nơi tập trung các chức năng chính giúp kết nối giữa các thành phần khác nhau của ứng dụng.

## Vai Trò
Thư mục `services` đóng vai trò như một tầng trung gian giữa các thành phần như API, cơ sở dữ liệu, và các mô hình tìm kiếm. Nó giúp:
1. **Tổ Chức Logic Nghiệp Vụ**: Tách biệt logic nghiệp vụ khỏi các thành phần khác, giúp mã nguồn dễ bảo trì.
2. **Tích Hợp Dữ Liệu**: Kết nối và xử lý dữ liệu từ nhiều nguồn khác nhau.
3. **Tăng Tính Mở Rộng**: Dễ dàng thêm mới hoặc chỉnh sửa các chức năng mà không ảnh hưởng đến các thành phần khác.

## Các Thành Phần Chính
Thư mục `services` thường bao gồm các file và module sau:
- **Data Processing Services**: Xử lý dữ liệu trước khi lưu trữ hoặc trả về cho người dùng.
- **Search Services**: Triển khai các thuật toán tìm kiếm và kết hợp kết quả từ nhiều phương pháp.
- **Integration Services**: Kết nối với các hệ thống bên ngoài như cơ sở dữ liệu, Elasticsearch, hoặc các API khác.

## Đánh Giá
Thư mục `services` được thiết kế tốt, giúp tổ chức mã nguồn một cách rõ ràng và dễ hiểu. Nó đóng vai trò quan trọng trong việc đảm bảo tính linh hoạt và hiệu quả của hệ thống.

---
