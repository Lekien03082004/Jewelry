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