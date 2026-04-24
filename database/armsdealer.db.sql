BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS brands (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    slug        TEXT    NOT NULL UNIQUE,
    logo_file   TEXT,
    description TEXT,
    is_active   INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS brands_translations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_id    INTEGER NOT NULL,
    lang_code   TEXT    NOT NULL,
    name        TEXT    NOT NULL,
    description TEXT,
    UNIQUE (brand_id, lang_code),
    FOREIGN KEY (brand_id)   REFERENCES brands(id)    ON DELETE CASCADE,
    FOREIGN KEY (lang_code)  REFERENCES languages(code)
);
CREATE TABLE IF NOT EXISTS cart_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    item_type   TEXT    NOT NULL DEFAULT 'product',
    item_id     INTEGER NOT NULL,
    quantity    INTEGER NOT NULL DEFAULT 1,
    added_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE (user_id, item_type, item_id)
);
CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    slug        TEXT    NOT NULL UNIQUE,
    type        TEXT    NOT NULL DEFAULT 'product',     -- 'product' | 'service'
    icon_file   TEXT,
    description TEXT
);
CREATE TABLE IF NOT EXISTS category_translations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    lang_code   TEXT    NOT NULL REFERENCES languages(code),
    name        TEXT    NOT NULL,
    description TEXT,
    UNIQUE (category_id, lang_code)
);
CREATE TABLE IF NOT EXISTS currencies (
    code        TEXT    PRIMARY KEY,
    symbol      TEXT    NOT NULL,
    label       TEXT    NOT NULL,
    rate_to_php REAL    NOT NULL DEFAULT 1.0,
    is_active   INTEGER NOT NULL DEFAULT 1,
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS inquiries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL,
    subject     TEXT,
    message     TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'new',            -- 'new' | 'read' | 'resolved'
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS languages (
    code        TEXT    PRIMARY KEY,
    label       TEXT    NOT NULL,
    locale      TEXT    NOT NULL,
    is_active   INTEGER NOT NULL DEFAULT 1,
    sort_order  INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS order_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id    INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    item_type   TEXT    NOT NULL DEFAULT 'product'
                CHECK (item_type IN ('product', 'service')),  -- 'product' | 'service'
    item_id     INTEGER NOT NULL,
    quantity    INTEGER NOT NULL DEFAULT 1,
    unit_price  REAL    NOT NULL
);
CREATE TABLE IF NOT EXISTS orders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    status      TEXT    NOT NULL DEFAULT 'pending',     -- 'pending' | 'verified' | 'paid' | 'shipped' | 'completed' | 'cancelled'
    total       REAL    NOT NULL DEFAULT 0,
    notes       TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS products (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT    NOT NULL,
    slug           TEXT    NOT NULL UNIQUE,
    category_id    INTEGER NOT NULL REFERENCES categories(id),
    subcategory_id INTEGER REFERENCES subcategories(id),
    brand_id       INTEGER REFERENCES brands(id),
    description    TEXT,
    price          REAL    NOT NULL,
    discount       REAL    DEFAULT 0,
    stock          INTEGER NOT NULL DEFAULT 0,
    rating         REAL    NOT NULL DEFAULT 0 CHECK (rating >= 0 AND rating <= 5),
    sales_count    INTEGER NOT NULL DEFAULT 0,
    image_file     TEXT,
    tags           TEXT,                                -- JSON array string
    is_featured    INTEGER NOT NULL DEFAULT 0,
    created_at     TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at     TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS products_translations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    lang_code   TEXT    NOT NULL REFERENCES languages(code),
    name        TEXT    NOT NULL,
    description TEXT,
    tags        TEXT,
    UNIQUE (product_id, lang_code)
);
CREATE TABLE IF NOT EXISTS services (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT    NOT NULL,
    slug           TEXT    NOT NULL UNIQUE,
    category_id    INTEGER NOT NULL REFERENCES categories(id),
    subcategory_id INTEGER REFERENCES subcategories(id),
    brand_id       INTEGER REFERENCES brands(id),
    description    TEXT,
    price          REAL    NOT NULL,
    discount       REAL    DEFAULT 0,
    rating         REAL    NOT NULL DEFAULT 0 CHECK (rating >= 0 AND rating <= 5),
    sales_count    INTEGER NOT NULL DEFAULT 0,
    image_file     TEXT,
    tags           TEXT,
    is_featured    INTEGER NOT NULL DEFAULT 0,
    created_at     TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at     TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS services_translations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id  INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    lang_code   TEXT    NOT NULL REFERENCES languages(code),
    name        TEXT    NOT NULL,
    description TEXT,
    tags        TEXT,
    UNIQUE (service_id, lang_code)
);
CREATE TABLE IF NOT EXISTS subcategories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    name        TEXT    NOT NULL,
    slug        TEXT    NOT NULL UNIQUE,
    icon_file   TEXT,
    description TEXT,
    UNIQUE (category_id, name)
);
CREATE TABLE IF NOT EXISTS subcategory_translations (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    subcategory_id INTEGER NOT NULL REFERENCES subcategories(id) ON DELETE CASCADE,
    lang_code      TEXT    NOT NULL REFERENCES languages(code),
    name           TEXT    NOT NULL,
    description    TEXT,
    UNIQUE (subcategory_id, lang_code)
);
CREATE TABLE IF NOT EXISTS ui_strings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    lang_code   TEXT    NOT NULL REFERENCES languages(code),
    key         TEXT    NOT NULL,
    value       TEXT    NOT NULL,
    UNIQUE (lang_code, key)
);
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL DEFAULT 'customer',   -- 'customer' | 'admin'
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);
INSERT INTO "categories" ("id","name","slug","type","icon_file","description") VALUES (1,'Firearms','firearms','product',NULL,'Guns and ranged weapons'),
 (2,'Blades','blades','product',NULL,'Knives, swords, and edged weapons'),
 (3,'Blunts','blunts','product',NULL,'Impact weapons like bats and clubs'),
 (4,'Projectile','projectile','product',NULL,'Bows, crossbows, and thrown weapons'),
 (5,'Explosives','explosives','product',NULL,'Explosive devices and materials'),
 (6,'Electronic','electronic','product',NULL,'Electronic warfare tools and devices'),
 (7,'Chemical','chemical','product',NULL,'Chemical-based tools or agents'),
 (8,'Biological','biological','product',NULL,'Biological-related materials'),
 (9,'Vehicle','vehicle','product',NULL,'Vehicles used in operations'),
 (10,'Cyber','cyber','product',NULL,'Cybersecurity and hacking tools'),
 (11,'Security','security','product',NULL,'Security-related equipment'),
 (12,'Ammunition','ammunition','product',NULL,'Bullets, shells, and cartridges'),
 (13,'Protective','protective','product',NULL,'Armor and protective gear'),
 (14,'Tactical','tactical','product',NULL,'Tactical gear and accessories'),
 (15,'Attachments','attachments','product',NULL,'Weapon attachments and add-ons'),
 (16,'Maintenance','maintenance-equipment','product',NULL,'Cleaning and repair tools'),
 (17,'Storage','storage-equipment','product',NULL,'Storage solutions'),
 (18,'Communication','communication','product',NULL,'Radios and communication tools'),
 (19,'Survival','survival','product',NULL,'Survival kits and gear'),
 (20,'Training','training-equipment','product',NULL,'Training tools and aids'),
 (21,'Manufacturing','manufacturing','service',NULL,'Production of equipment and tools'),
 (22,'Customization','customization','service',NULL,'Custom modifications and builds'),
 (23,'Maintenance ','maintenance-service','service',NULL,'Repair and upkeep services'),
 (24,'Transport','transport','service',NULL,'Logistics and transport services'),
 (25,'Storage Services','storage-service','service',NULL,'Secure storage services'),
 (26,'Training Services','training-service','service',NULL,'Skill and operational training'),
 (27,'Protection','protection','service',NULL,'Security and protection services'),
 (28,'Consulting','consulting','service',NULL,'Expert advice and planning'),
 (29,'Research','research','service',NULL,'Research and development'),
 (30,'Testing','testing','service',NULL,'Product and system testing'),
 (31,'Disposal','disposal','service',NULL,'Safe disposal services'),
 (32,'Surveillance','surveillance','service',NULL,'Monitoring and surveillance'),
 (33,'Contracting','contracting','service',NULL,'Contract-based operations');
INSERT INTO "category_translations" ("id","category_id","lang_code","name","description") VALUES (1,1,'filipino','Mga Baril','Mga baril at sandata sa malayo'),
 (2,2,'filipino','Mga Talim','Mga kutsilyo, espada, at matutulis na sandata'),
 (3,3,'filipino','Mga Pamalo','Mga sandata sa pagpukpok tulad ng bat at pamalo'),
 (4,4,'filipino','Proyektil','Busog, crossbow, at mga itinatapon na sandata'),
 (5,5,'filipino','Mga Pagsabog','Mga pagsabog na kagamitan at materyales'),
 (6,6,'filipino','Elektroniko','Mga kagamitan at aparato para sa elektronikong digmaan'),
 (7,7,'filipino','Kemikal','Mga kagamitan o ahente na nakabatay sa kemikal'),
 (8,8,'filipino','Biyolohikal','Mga materyales na may kaugnayan sa biyolohiya'),
 (9,9,'filipino','Sasakyan','Mga sasakyan na ginagamit sa mga operasyon'),
 (10,10,'filipino','Cyber','Mga kagamitan sa cybersecurity at pag-hack'),
 (11,11,'filipino','Seguridad','Mga kagamitan na may kaugnayan sa seguridad'),
 (12,12,'filipino','Bala','Mga bala, shell, at kartutso'),
 (13,13,'filipino','Protektibo','Armor at mga kagamitang pangproteksiyon'),
 (14,14,'filipino','Taktikal','Mga taktikal na kagamitan at aksesorya'),
 (15,15,'filipino','Mga Attachment','Mga attachment at dagdag sa sandata'),
 (16,16,'filipino','Pagpapanatili','Mga kagamitan sa paglilinis at pagkukumpuni'),
 (17,17,'filipino','Imbakan','Mga solusyon sa imbakan'),
 (18,18,'filipino','Komunikasyon','Mga radyo at kagamitan sa komunikasyon'),
 (19,19,'filipino','Kaligtasan','Mga survival kit at kagamitan'),
 (20,20,'filipino','Pagsasanay','Mga kagamitan at tulong sa pagsasanay'),
 (21,21,'filipino','Pagmamanupaktura','Produksyon ng mga kagamitan at kasangkapan'),
 (22,22,'filipino','Kustomisasyon','Mga pasadyang pagbabago at gawa'),
 (23,23,'filipino','Serbisyo sa Pagpapanatili','Mga serbisyo sa pagkukumpuni at pag-aalaga'),
 (24,24,'filipino','Transportasyon','Mga serbisyo sa logistik at transportasyon'),
 (25,25,'filipino','Serbisyo sa Imbakan','Mga ligtas na serbisyo sa imbakan'),
 (26,26,'filipino','Serbisyo sa Pagsasanay','Pagsasanay sa kasanayan at operasyon'),
 (27,27,'filipino','Proteksyon','Mga serbisyo sa seguridad at proteksyon'),
 (28,28,'filipino','Konsultasyon','Dalubhasang payo at pagpaplano'),
 (29,29,'filipino','Pananaliksik','Pananaliksik at pagpapaunlad'),
 (30,30,'filipino','Pagsubok','Pagsubok ng produkto at sistema'),
 (31,31,'filipino','Pagtatapon','Mga ligtas na serbisyo sa pagtatapon'),
 (32,32,'filipino','Pagmamasid','Pagmamatyag at pagsubaybay'),
 (33,33,'filipino','Kontratista','Mga operasyong batay sa kontrata'),
 (34,1,'japanese','銃器','銃および遠距離兵器'),
 (35,2,'japanese','刃物','ナイフ、剣、および刃物系武器'),
 (36,3,'japanese','鈍器','バットや棍棒などの打撃武器'),
 (37,4,'japanese','飛道具','弓、クロスボウ、および投擲武器'),
 (38,5,'japanese','爆発物','爆発装置および爆発物資'),
 (39,6,'japanese','電子機器','電子戦ツールおよびデバイス'),
 (40,7,'japanese','化学兵器','化学物質を用いたツールまたは薬剤'),
 (41,8,'japanese','生物兵器','生物関連素材'),
 (42,9,'japanese','車両','作戦で使用される車両'),
 (43,10,'japanese','サイバー','サイバーセキュリティおよびハッキングツール'),
 (44,11,'japanese','セキュリティ','セキュリティ関連機器'),
 (45,12,'japanese','弾薬','弾丸、砲弾、およびカートリッジ'),
 (46,13,'japanese','防護具','アーマーおよび防護装備'),
 (47,14,'japanese','戦術装備','戦術ギアおよびアクセサリー'),
 (48,15,'japanese','アタッチメント','武器アタッチメントおよびアドオン'),
 (49,16,'japanese','メンテナンス','清掃および修理ツール'),
 (50,17,'japanese','保管','保管ソリューション'),
 (51,18,'japanese','通信','無線機および通信ツール'),
 (52,19,'japanese','サバイバル','サバイバルキットおよび装備'),
 (53,20,'japanese','トレーニング','トレーニングツールおよび補助具'),
 (54,21,'japanese','製造','機器およびツールの生産'),
 (55,22,'japanese','カスタマイズ','カスタム改造およびビルド'),
 (56,23,'japanese','メンテナンスサービス','修理および維持管理サービス'),
 (57,24,'japanese','輸送','物流および輸送サービス'),
 (58,25,'japanese','保管サービス','安全な保管サービス'),
 (59,26,'japanese','トレーニングサービス','スキルおよび作戦トレーニング'),
 (60,27,'japanese','警護','セキュリティおよび保護サービス'),
 (61,28,'japanese','コンサルティング','専門的なアドバイスと計画'),
 (62,29,'japanese','研究','研究および開発'),
 (63,30,'japanese','テスト','製品およびシステムのテスト'),
 (64,31,'japanese','廃棄','安全な廃棄サービス'),
 (65,32,'japanese','監視','モニタリングおよび監視'),
 (66,33,'japanese','契約業務','契約に基づく業務'),
 (67,1,'spanish','Armas de Fuego','Pistolas y armas de largo alcance'),
 (68,2,'spanish','Armas Blancas','Cuchillos, espadas y armas con filo'),
 (69,3,'spanish','Armas Contundentes','Armas de impacto como bates y porras'),
 (70,4,'spanish','Proyectiles','Arcos, ballestas y armas arrojadizas'),
 (71,5,'spanish','Explosivos','Dispositivos y materiales explosivos'),
 (72,6,'spanish','Electrónico','Herramientas y dispositivos de guerra electrónica'),
 (73,7,'spanish','Químico','Herramientas o agentes de base química'),
 (74,8,'spanish','Biológico','Materiales relacionados con agentes biológicos'),
 (75,9,'spanish','Vehículos','Vehículos utilizados en operaciones'),
 (76,10,'spanish','Cibernético','Herramientas de ciberseguridad y hacking'),
 (77,11,'spanish','Seguridad','Equipos relacionados con la seguridad'),
 (78,12,'spanish','Munición','Balas, proyectiles y cartuchos'),
 (79,13,'spanish','Protector','Armadura y equipo de protección'),
 (80,14,'spanish','Táctico','Equipo táctico y accesorios'),
 (81,15,'spanish','Accesorios','Accesorios y complementos para armas'),
 (82,16,'spanish','Mantenimiento','Herramientas de limpieza y reparación'),
 (83,17,'spanish','Almacenamiento','Soluciones de almacenamiento'),
 (84,18,'spanish','Comunicación','Radios y herramientas de comunicación'),
 (85,19,'spanish','Supervivencia','Kits y equipo de supervivencia'),
 (86,20,'spanish','Entrenamiento','Herramientas y ayudas de entrenamiento'),
 (87,21,'spanish','Fabricación','Producción de equipos y herramientas'),
 (88,22,'spanish','Personalización','Modificaciones y construcciones personalizadas'),
 (89,23,'spanish','Servicio de Mantenimiento','Servicios de reparación y mantenimiento'),
 (90,24,'spanish','Transporte','Servicios de logística y transporte'),
 (91,25,'spanish','Servicios de Almacenamiento','Servicios de almacenamiento seguro'),
 (92,26,'spanish','Servicios de Entrenamiento','Entrenamiento de habilidades y operaciones'),
 (93,27,'spanish','Protección','Servicios de seguridad y protección'),
 (94,28,'spanish','Consultoría','Asesoramiento experto y planificación'),
 (95,29,'spanish','Investigación','Investigación y desarrollo'),
 (96,30,'spanish','Pruebas','Pruebas de productos y sistemas'),
 (97,31,'spanish','Eliminación','Servicios de eliminación segura'),
 (98,32,'spanish','Vigilancia','Monitoreo y vigilancia'),
 (99,33,'spanish','Contratación','Operaciones basadas en contratos'),
 (100,1,'mandarin','枪械','枪支和远程武器'),
 (101,2,'mandarin','刀刃','刀具、剑及刃器武器'),
 (102,3,'mandarin','钝器','球棒和棍棒等冲击性武器'),
 (103,4,'mandarin','投射物','弓、弩及投掷武器'),
 (104,5,'mandarin','爆炸物','爆炸装置及材料'),
 (105,6,'mandarin','电子设备','电子战工具和设备'),
 (106,7,'mandarin','化学品','化学类工具或制剂'),
 (107,8,'mandarin','生物材料','与生物相关的材料'),
 (108,9,'mandarin','车辆','用于行动的车辆'),
 (109,10,'mandarin','网络','网络安全和黑客工具'),
 (110,11,'mandarin','安保','安保相关设备'),
 (111,12,'mandarin','弹药','子弹、炮弹和弹筒'),
 (112,13,'mandarin','防护装备','盔甲和防护装备'),
 (113,14,'mandarin','战术装备','战术装备和配件'),
 (114,15,'mandarin','附件','武器附件和配件'),
 (115,16,'mandarin','维护','清洁和修理工具'),
 (116,17,'mandarin','存储','存储解决方案'),
 (117,18,'mandarin','通信','无线电和通信工具'),
 (118,19,'mandarin','生存','生存套件和装备'),
 (119,20,'mandarin','训练','训练工具和辅助设备'),
 (120,21,'mandarin','制造','设备和工具的生产'),
 (121,22,'mandarin','定制','定制改装和制造'),
 (122,23,'mandarin','维护服务','维修和保养服务'),
 (123,24,'mandarin','运输','物流和运输服务'),
 (124,25,'mandarin','存储服务','安全存储服务'),
 (125,26,'mandarin','培训服务','技能和作战培训'),
 (126,27,'mandarin','保护','安保和保护服务'),
 (127,28,'mandarin','咨询','专家建议和规划'),
 (128,29,'mandarin','研究','研究和开发'),
 (129,30,'mandarin','测试','产品和系统测试'),
 (130,31,'mandarin','处置','安全处置服务'),
 (131,32,'mandarin','监控','监测和监视'),
 (132,33,'mandarin','承包','基于合同的运营');
INSERT INTO "currencies" ("code","symbol","label","rate_to_php","is_active","updated_at") VALUES ('PHP','₱','PHP (₱)',1.0,1,'2026-04-24 03:34:57'),
 ('USD','$','USD ($)',0.0175,1,'2026-04-24 03:34:57'),
 ('EUR','€','EUR (€)',0.0162,1,'2026-04-24 03:34:57'),
 ('JPY','¥','JPY (JP¥)',2.627,1,'2026-04-14 06:58:41'),
 ('CNY','¥','CNY (CN¥)',0.127,1,'2026-04-14 06:58:41');
INSERT INTO "languages" ("code","label","locale","is_active","sort_order") VALUES ('english','English','en',1,1),
 ('filipino','Filipino','fil',1,2),
 ('japanese','Japanese','ja',1,3),
 ('spanish','Spanish','es',1,4),
 ('mandarin','Mandarin','zh',1,5);
INSERT INTO "users" ("id","username","email","password_hash","role","created_at","updated_at") VALUES (1,'spongebob','spongebob@bikini.bottom','scrypt:32768:8:1$SbTwSrAmCehypPz8$1fd49b243228a73c60f77f4fd51cf7f46d77f044b2576a24fe7de1800ca3dabe891e693f64f2276ef392437527659822711cb089f651944ef50073f5188a0c42','customer','2026-04-15 05:03:32','2026-04-15 05:03:32'),
 (2,'mrcrabs','eugene.crabs@thekrustykrab.com','scrypt:32768:8:1$83oDsOSmvXx89UZx$c0e15772d19273f1df094dffa5fb9846afa2be3bfa47bb50a89d3ec80c57032db06799f09fb4b4d51be28dfb33de4148c29c7b97396f1dbbaba90920d6b78dc3','admin','2026-04-15 05:03:32','2026-04-15 05:03:32'),
 (3,'KelsenGile','kelsengilesarmientoconel@gmail.com','scrypt:32768:8:1$XrzCLf0eixrrKiHF$94eee8816393d6c3fde4901ccd40f36f33d5fed9031cf15212b3a3acc91d25a7b11b7f9295ade278f201088b7c0e87f1242b859b5fc2008aaba577a9d9babdd2','customer','2026-04-15 07:00:44','2026-04-15 07:00:44');
CREATE INDEX idx_order_items_order  ON order_items   (order_id);
CREATE INDEX idx_orders_status      ON orders        (status);
CREATE INDEX idx_orders_user        ON orders        (user_id);
CREATE INDEX idx_products_brand     ON products      (brand_id);
CREATE INDEX idx_products_category  ON products      (category_id);
CREATE INDEX idx_products_subcat    ON products      (subcategory_id);
CREATE INDEX idx_services_brand     ON services      (brand_id);
CREATE INDEX idx_services_category  ON services      (category_id);
CREATE INDEX idx_services_subcat    ON services      (subcategory_id);
CREATE INDEX idx_subcats_category   ON subcategories (category_id);
CREATE INDEX idx_ui_strings_lang    ON ui_strings    (lang_code);
CREATE TRIGGER trg_order_completed
AFTER UPDATE OF status ON orders
WHEN NEW.status = 'completed' AND OLD.status != 'completed'
BEGIN
    UPDATE products
    SET sales_count = sales_count + (
        SELECT COALESCE(SUM(oi.quantity), 0)
        FROM order_items oi
        WHERE oi.order_id = NEW.id
          AND oi.item_type = 'product'
          AND oi.item_id = products.id
    )
    WHERE id IN (
        SELECT item_id FROM order_items
        WHERE order_id = NEW.id AND item_type = 'product'
    );

    UPDATE services
    SET sales_count = sales_count + (
        SELECT COALESCE(SUM(oi.quantity), 0)
        FROM order_items oi
        WHERE oi.order_id = NEW.id
          AND oi.item_type = 'service'
          AND oi.item_id = services.id
    )
    WHERE id IN (
        SELECT item_id FROM order_items
        WHERE order_id = NEW.id AND item_type = 'service'
    );
END;
CREATE TRIGGER trg_order_uncompleted
AFTER UPDATE OF status ON orders
WHEN OLD.status = 'completed' AND NEW.status != 'completed'
BEGIN
    UPDATE products
    SET sales_count = MAX(0, sales_count - (
        SELECT COALESCE(SUM(oi.quantity), 0)
        FROM order_items oi
        WHERE oi.order_id = NEW.id
          AND oi.item_type = 'product'
          AND oi.item_id = products.id
    ))
    WHERE id IN (
        SELECT item_id FROM order_items
        WHERE order_id = NEW.id AND item_type = 'product'
    );

    UPDATE services
    SET sales_count = MAX(0, sales_count - (
        SELECT COALESCE(SUM(oi.quantity), 0)
        FROM order_items oi
        WHERE oi.order_id = NEW.id
          AND oi.item_type = 'service'
          AND oi.item_id = services.id
    ))
    WHERE id IN (
        SELECT item_id FROM order_items
        WHERE order_id = NEW.id AND item_type = 'service'
    );
END;
COMMIT;
