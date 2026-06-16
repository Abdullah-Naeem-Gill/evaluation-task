## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/`.


- **Anonymous users** may only `GET /api/products/`.
- **Authenticated customers** may place orders, list and view their own orders, and cancel their own pending orders.
- **Staff users** (`is_staff=True`) may create products, view all orders, access any order detail, and cancel any pending order.

Use `createsuperuser` for a staff account. Create regular users via Django admin or `createsuperuser` with `is_staff=False`.

```bash
curl -u username:password http://127.0.0.1:8000/api/orders/
```

## API Endpoints

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/products/` | Public | List products. Search: `?search=` (name, sku). Filter: `?in_stock=true` or `?in_stock=false` |
| POST | `/api/products/` | Staff | Create a product |
| GET | `/api/orders/` | Authenticated | List orders (own orders for customers, all for staff). Includes nested items and computed `total` |
| POST | `/api/orders/` | Authenticated | Create an order with one or more items |
| GET | `/api/orders/{id}/` | Authenticated | Order detail (own order or any for staff) |
| POST | `/api/orders/{id}/cancel/` | Authenticated | Cancel a pending order and restock items |

### Order cancellation

Only orders with status `pending` can be cancelled. Orders that are `paid`, `shipped`, or already `cancelled` are rejected with a 400 error. Cancelling a pending order restocks all of its items atomically.

Duplicate product lines in a single create-order payload are merged before stock validation (e.g. two lines for the same product with quantity 1 each are treated as one line with quantity 2).

## Migration Story

The `products` app migrations document an intentional field rename:

1. **0001_initial** — Creates `Product` with `quantity_on_hand` (not `stock_quantity`). All domain models are introduced across `products` and `orders` migrations.
2. **0002_seed_products** — `RunPython` data migration inserts sample products using `quantity_on_hand`. No fixtures or external scripts.
3. **0003_rename_quantity_on_hand_stock_quantity** — `RenameField` from `quantity_on_hand` to `stock_quantity`, preserving seeded data.

After `python manage.py migrate` on a fresh database, seeded products retain their original stock values under `stock_quantity`. All application code references `stock_quantity` only.

