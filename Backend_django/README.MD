Action	HTTP method	DRF class
Create	POST	CreateAPIView
Read list	GET	ListAPIView
Read 1	GET	RetrieveAPIView
Update	PUT/PATCH	UpdateAPIView
Delete	DELETE	DestroyAPIView


✅ RetrieveUpdateDestroyAPIView làm được gì?

Trong Django REST Framework, class này hỗ trợ sẵn:

Method	Action
GET	retrieve (lấy 1 object)
PUT	update (cập nhật toàn bộ)
PATCH	partial_update (cập nhật 1 phần)
DELETE	destroy (xóa)


Bảng	Nên dùng
users	ViewSet
products	ViewSet
categories	ViewSet / ReadOnly
cart_items	APIView / Generic
orders	⚠️ Generic + APIView
order_items	❌ không cần riêng
reviews	ViewSet
wishlist	ViewSet / APIView



Method	Tác dụng
get_<field_name>(self, obj)	                Tính toán giá trị cho SerializerMethodField
validate_<field_name>(self, value)	        Validate một field cụ thể
validate(self, data)	                    Validate nhiều field cùng lúc
create(self, validated_data)	            Tùy chỉnh logic tạo mới dữ liệu
update(self, instance, validated_data)	    Tùy chỉnh logic cập nhật dữ liệu
to_representation(self, instance)	        Tùy chỉnh dữ liệu trả về JSON
to_internal_value(self, data)	            Tùy chỉnh dữ liệu nhận vào trước khi validate
get_fields(self)	                        Thêm/xóa/sửa field động
get_queryset(self)	                        Tùy chỉnh queryset trong View/ViewSet
get_serializer_class(self)	                Chọn serializer khác nhau theo action
perform_create(self, serializer)	        Thêm logic khi tạo dữ liệu trong ViewSet
perform_update(self, serializer)	        Thêm logic khi cập nhật dữ liệu trong ViewSet
perform_destroy(self, instance)	            Thêm logic khi xóa dữ liệu trong ViewSet
get_permissions(self)	                    Phân quyền động theo action
get_serializer_context(self)	            Truyền thêm dữ liệu vào serializer
list(self, request)	                        Ghi đè API lấy danh sách
retrieve(self, request, pk=None)	        Ghi đè API lấy chi tiết
create(self, request) (ViewSet)         	Ghi đè API POST
update(self, request, pk=None) (ViewSet)	Ghi đè API PUT
partial_update(self, request, pk=None)	    Ghi đè API PATCH
destroy(self, request, pk=None)	            Ghi đè API DELETE