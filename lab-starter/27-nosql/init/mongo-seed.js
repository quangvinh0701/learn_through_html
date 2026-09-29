// =============================================================
// Lab 27 — init/mongo-seed.js
// Chay TU DONG mot lan khi volume mongo_data duoc khoi tao lan dau
//   (mount vao /docker-entrypoint-initdb.d/01-seed.js).
// Muon chay lai: docker compose down -v && docker compose up -d
//
// Trich & chuyen the tu 27-nosql-distributed-storage-masterclass.html
//   (Chuong 16, buoc 3 "MongoDB — catalog san pham").
// =============================================================

// Script trong /docker-entrypoint-initdb.d chay voi quyen root va o db
// duoc chi dinh boi MONGO_INITDB_DATABASE. getSiblingDB cho chac chan.
const shop = db.getSiblingDB('shop');

// ── 1. Xoa sach neu chay lai bang tay ──
shop.products.drop();
shop.orders_snapshot.drop();

// ── 2. Catalog san pham: CO Y de thuoc tinh khong dong nhat ──
// Diem hoc: mot collection, nhieu "hinh dang" tai lieu. Do la suc manh
// cua document store va cung la nguon goc moi rac roi ha nguon (Chuong 15).
shop.products.insertMany([
  { _id: 'P-001', name: 'Ao thun cotton', category: 'apparel', price: 199000,
    in_stock: true,
    attrs: { size: ['S','M','L'], color: 'navy', material: 'cotton' },
    variants: [ { sku: 'P-001-S', qty: 12 }, { sku: 'P-001-M', qty: 30 } ],
    updated_at: new Date('2026-07-01T10:00:00Z') },

  { _id: 'P-002', name: 'Tai nghe BT', category: 'electronics', price: 890000,
    in_stock: true,
    attrs: { battery_mah: 400, bluetooth: '5.3', warranty_months: 12 },
    variants: [ { sku: 'P-002-BLK', qty: 5 } ],
    updated_at: new Date('2026-07-02T08:30:00Z') },

  // BAY SO 1: price ghi bang CHUOI. Khong co gi chan lai o tang DB.
  { _id: 'P-003', name: 'Ca phe rang moc', category: 'grocery', price: '145000',
    in_stock: false,
    attrs: { weight_g: 250, roast: 'medium', origin: 'Da Lat' },
    updated_at: new Date('2026-07-02T09:15:00Z') },

  // BAY SO 2: THIEU han truong in_stock. Query {in_stock: false} bo sot doc nay.
  { _id: 'P-004', name: 'Ban phim co', category: 'electronics', price: 1590000,
    attrs: { switch: 'brown', layout: '75%', warranty_months: 24, rgb: true },
    variants: [ { sku: 'P-004-BR', qty: 3 }, { sku: 'P-004-BL', qty: 0 },
                { sku: 'P-004-RD', qty: 7 } ],
    promo: { code: 'SUMMER', discount_pct: 15 },
    updated_at: new Date('2026-07-03T11:00:00Z') },

  { _id: 'P-005', name: 'Sach he phan tan', category: 'books', price: 320000,
    in_stock: true,
    attrs: { pages: 614, isbn: '978-1449373320', language: 'en' },
    updated_at: new Date('2026-07-03T12:00:00Z') },

  // BAY SO 3: truong di san legacy_price_vnd chi con o 1 tai lieu.
  { _id: 'P-006', name: 'Chuot khong day', category: 'electronics', price: 450000,
    in_stock: true,
    attrs: { dpi: 16000, battery_mah: 500, warranty_months: 12 },
    variants: [ { sku: 'P-006-WH', qty: 22 } ],
    legacy_price_vnd: 460000,
    updated_at: new Date('2026-06-28T07:00:00Z') },

  { _id: 'P-007', name: 'Binh giu nhiet', category: 'home', price: 275000,
    in_stock: true,
    attrs: { volume_ml: 500, material: 'inox 304' },
    updated_at: new Date('2026-07-04T06:00:00Z') },

  { _id: 'P-008', name: 'Man hinh 27 inch', category: 'electronics', price: 6200000,
    in_stock: false,
    attrs: { panel: 'IPS', refresh_hz: 144, warranty_months: 36, resolution: '2560x1440' },
    variants: [ { sku: 'P-008-STD', qty: 0 } ],
    promo: { code: 'BACK2WORK', discount_pct: 8 },
    updated_at: new Date('2026-07-04T09:45:00Z') }
]);

// ── 3. Chi muc: dat theo ACCESS PATTERN da liet ke, khong dat theo cam tinh ──
// AP-3 "liet ke san pham 1 danh muc, sap theo gia" -> compound (category, price)
shop.products.createIndex({ category: 1, price: 1 }, { name: 'cat_price' });

// AP-4 "loc theo thoi han bao hanh" -> chi 4/8 tai lieu co truong nay,
// sparse: true de chi muc khong luu 4 entry NULL vo ich.
shop.products.createIndex({ 'attrs.warranty_months': 1 },
                          { name: 'warranty', sparse: true });

// AP-9 "tim theo ten" -> text index. Luu y: MongoDB chi cho MOT text index
// moi collection, va no khong thay the duoc Elasticsearch (Chuong 10).
shop.products.createIndex({ name: 'text' }, { name: 'name_text',
                                              default_language: 'none' });

// ── 4. Collection phuc vu: ket qua tinh san tu warehouse do xuong ──
// Mau "tinh theo lo, phuc vu theo khoa" (Chuong 15, muc 3).
shop.orders_snapshot.insertMany([
  { _id: 'C-01', orders_30d: 3, gmv_30d: 1613000, tier: 'gold',
    computed_at: new Date('2026-07-30T02:00:00Z') },
  { _id: 'C-02', orders_30d: 1, gmv_30d: 1590000, tier: 'silver',
    computed_at: new Date('2026-07-30T02:00:00Z') },
  { _id: 'C-03', orders_30d: 1, gmv_30d: 6200000, tier: 'gold',
    computed_at: new Date('2026-07-30T02:00:00Z') }
]);

// ── 5. Kiem chung ngay tai cho ──
print('---- mongo-seed.js ----');
print('products          : ' + shop.products.countDocuments({}));
print('co in_stock       : ' + shop.products.countDocuments({ in_stock: { $exists: true } }) + '/8');
print('co variants       : ' + shop.products.countDocuments({ variants: { $exists: true } }) + '/8');
print('co promo          : ' + shop.products.countDocuments({ promo: { $exists: true } }) + '/8');
print('price kieu chuoi  : ' + shop.products.countDocuments({ price: { $type: 'string' } }));
print('orders_snapshot   : ' + shop.orders_snapshot.countDocuments({}));
print('indexes           : ' + shop.products.getIndexes().map(i => i.name).join(', '));
