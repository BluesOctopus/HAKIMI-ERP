# 客户管理模块（Customer Management）数据库设计说明

**—— 交接给 Codex 的实现与测试依据文档**

| 项 | 内容 |
| --- | --- |
| 文档目的 | 向 Codex 说明客户管理模块的数据库设计，作为其实现、修改与测试该模块的唯一权威依据 |
| 模块范围 | 客户管理（Customer Management）全模块：D1 客户主数据 5 张表 + D2 物料主数据 1 张表 |
| 明确排除 | D3 业务单据、D4 物流、D5 财务（本期不实现、不测试，仅作为外部引用方说明其影响） |
| 数据库环境 | MySQL 8.0+ / InnoDB / utf8mb4 |
| 依据文档 | 《系统设计报告》第二部分第 3、4 章（数据库设计）、第三部分 3.1–3.2 节（API 契约）、第一部分 4.2 / 4.7 / 5.1 节（原型与校验规范） |
| 定稿脚本 | `sap_sd_d124.sql`（本模块相关段落已完整收录于本文第 2 章） |

---

## 第1章 模块全景

### 1.1 菜单与数据表映射

客户管理模块在系统中的菜单结构及其对应数据表：

| 菜单项 | 对应原型 | 涉及物理表 |
| --- | --- | --- |
| Customer Management → Business Partner | 4.2 创建业务伙伴（Create Business Partner） | business_partner、contact、bp_relationship |
| （扩展视图维护） | — | customer_sales_data、customer_finance_data |
| 全局组件：F4 搜索帮助弹窗 | 4.7 Relationship Category | bp_relationship |
| Customer Management → Material | — | material |

### 1.2 表清单与职责

| 表名 | 中文含义 | 职责 |
| --- | --- | --- |
| business_partner | 业务伙伴（客户主记录） | 客户主体，一客户一条主记录 |
| customer_sales_data | 客户销售区域数据 | 按销售区域（销售组织/分销渠道/产品组）扩展的销售视图 |
| customer_finance_data | 客户公司代码财务数据 | 按公司代码扩展的财务视图（银行、支付卡、统驭科目） |
| contact | 联系人 | 客户下属联系人，1 : n |
| bp_relationship | 业务伙伴关系 | 伙伴之间有向关系（集团-子公司、雇主-雇员等） |
| material | 物料主记录 | 物料主数据，被各单据行项目引用 |

### 1.3 关系结构

```
business_partner ──1:n── customer_sales_data     （按销售区域，复合主键）
               ──1:n── customer_finance_data    （按公司代码，复合主键）
               ──1:n── contact
               ──1:n── bp_relationship          （bp_from / bp_to 双外键自引用）

material ──被引用── D3/D4/D5 全部行项目表（ON DELETE RESTRICT，本期仅作为外部依赖了解）
```

设计理念：采用 SAP Business Partner 模式——同一客户主体只存一条主记录，其承担的不同角色（售达方/送达方/付款方）、不同销售区域视图、不同公司代码视图分别扩展为从表，避免基础信息冗余。

---

## 第2章 建库脚本（定稿 DDL，可直接执行）

以下脚本摘自 `sap_sd_d124.sql` 中本模块相关段落，建表顺序已按外键依赖排好，可整体执行。

```sql
-- ==================== D1 客户主数据 ====================

CREATE TABLE business_partner (
    bp_id               VARCHAR(20)  NOT NULL COMMENT '业务伙伴编号',
    bp_type             VARCHAR(10)  NOT NULL,
    bp_role             VARCHAR(10)  NOT NULL COMMENT '角色:售达方/送达方/付款方',
    bp_name             VARCHAR(80)  NOT NULL,
    country             CHAR(2),
    city                VARCHAR(40),
    district            VARCHAR(40),
    street              VARCHAR(60),
    house_number        VARCHAR(10),
    postal_code         VARCHAR(10),
    language            CHAR(2),
    time_zone           VARCHAR(10),
    transportation_zone VARCHAR(10),
    telephone           VARCHAR(20),
    mobile_phone        VARCHAR(20),
    fax                 VARCHAR(20),
    email               VARCHAR(80),
    status              VARCHAR(10)  NOT NULL DEFAULT 'ACTIVE',
    block_reason        VARCHAR(20),
    permission_group    VARCHAR(10),
    data_source         VARCHAR(10),
    print_format        VARCHAR(10),
    created_time        DATETIME     DEFAULT CURRENT_TIMESTAMP,
    last_changed_time   DATETIME     DEFAULT CURRENT_TIMESTAMP
                                     ON UPDATE CURRENT_TIMESTAMP,
    remark              VARCHAR(255),
    search_term         VARCHAR(100),
    CONSTRAINT pk_business_partner PRIMARY KEY (bp_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_bp_name    ON business_partner (bp_name);
CREATE INDEX idx_bp_region  ON business_partner (country, city);
CREATE INDEX idx_bp_status  ON business_partner (status);
CREATE INDEX idx_bp_changed ON business_partner (last_changed_time);


CREATE TABLE customer_sales_data (
    bp_id                      VARCHAR(20) NOT NULL,
    sales_org                  VARCHAR(10) NOT NULL,
    distribution_channel       VARCHAR(10) NOT NULL,
    division                   VARCHAR(10) NOT NULL,
    sales_office               VARCHAR(10),
    sales_group                VARCHAR(10),
    sales_district             VARCHAR(10),
    currency                   CHAR(3),
    price_group                VARCHAR(10),
    customer_pricing_procedure VARCHAR(10),
    customer_statistics_group  VARCHAR(10),
    delivery_priority          VARCHAR(10),
    shipping_condition         VARCHAR(10),
    delivering_plant           VARCHAR(10),
    max_partial_deliveries     INT,
    incoterms                  VARCHAR(10),
    incoterms_location         VARCHAR(70),
    account_assignment_group   VARCHAR(10),
    tax_classification         VARCHAR(10),
    remark                     VARCHAR(255),
    search_term                VARCHAR(100),
    CONSTRAINT pk_customer_sales_data
        PRIMARY KEY (bp_id, sales_org, distribution_channel, division),
    CONSTRAINT fk_csd_bp FOREIGN KEY (bp_id)
        REFERENCES business_partner (bp_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_csd_area  ON customer_sales_data
    (sales_org, distribution_channel, division);
CREATE INDEX idx_csd_plant ON customer_sales_data (delivering_plant);


CREATE TABLE customer_finance_data (
    bp_id                  VARCHAR(20) NOT NULL,
    company_code           VARCHAR(10) NOT NULL,
    reconciliation_account VARCHAR(10),
    sort_key               VARCHAR(10),
    payment_terms          VARCHAR(10),
    bank_account_name      VARCHAR(80),
    bank_country           CHAR(2),
    bank_key               VARCHAR(15),
    bank_account           VARCHAR(18),
    iban                   VARCHAR(34),
    bank_account_status    VARCHAR(10),
    card_type              VARCHAR(10),
    card_number            VARCHAR(20),
    preferred_card         CHAR(1),
    card_status            VARCHAR(10),
    remark                 VARCHAR(255),
    search_term            VARCHAR(100),
    CONSTRAINT pk_customer_finance_data PRIMARY KEY (bp_id, company_code),
    CONSTRAINT fk_cfd_bp FOREIGN KEY (bp_id)
        REFERENCES business_partner (bp_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_cfd_company ON customer_finance_data (company_code);
CREATE INDEX idx_cfd_recon   ON customer_finance_data (reconciliation_account);


CREATE TABLE contact (
    contact_id         VARCHAR(20) NOT NULL,
    bp_id              VARCHAR(20) NOT NULL,
    contact_type       VARCHAR(10),
    contact_role       VARCHAR(10),
    first_name         VARCHAR(40),
    last_name          VARCHAR(40),
    birth_name         VARCHAR(40),
    country            CHAR(2),
    city               VARCHAR(40),
    district           VARCHAR(40),
    street             VARCHAR(60),
    house_number       VARCHAR(10),
    postal_code        VARCHAR(10),
    language           CHAR(2),
    time_zone          VARCHAR(10),
    status             VARCHAR(10),
    personal_phone     VARCHAR(20),
    wechat             VARCHAR(40),
    linkedin           VARCHAR(80),
    gender             CHAR(1),
    marital_status     VARCHAR(10),
    nationality        CHAR(2),
    former_nationality CHAR(2),
    birthday           DATE,
    birth_place        VARCHAR(60),
    occupation         VARCHAR(40),
    department         VARCHAR(40),
    position           VARCHAR(40),
    remark             VARCHAR(255),
    search_term        VARCHAR(100),
    CONSTRAINT pk_contact PRIMARY KEY (contact_id),
    CONSTRAINT fk_contact_bp FOREIGN KEY (bp_id)
        REFERENCES business_partner (bp_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_contact_bp    ON contact (bp_id);
CREATE INDEX idx_contact_name  ON contact (last_name, first_name);
CREATE INDEX idx_contact_phone ON contact (personal_phone);


CREATE TABLE bp_relationship (
    relation_id       VARCHAR(20) NOT NULL,
    relationship_type VARCHAR(10) NOT NULL,
    valid_from        DATE,
    valid_to          DATE,
    bp_from           VARCHAR(20) NOT NULL,
    bp_to             VARCHAR(20) NOT NULL,
    remark            VARCHAR(255),
    search_term       VARCHAR(100),
    CONSTRAINT pk_bp_relationship PRIMARY KEY (relation_id),
    CONSTRAINT fk_rel_from FOREIGN KEY (bp_from)
        REFERENCES business_partner (bp_id) ON DELETE RESTRICT,
    CONSTRAINT fk_rel_to FOREIGN KEY (bp_to)
        REFERENCES business_partner (bp_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_rel_from  ON bp_relationship (bp_from, relationship_type);
CREATE INDEX idx_rel_to    ON bp_relationship (bp_to, relationship_type);
CREATE INDEX idx_rel_valid ON bp_relationship (valid_from, valid_to);

-- ==================== D2 物料主数据 ====================

CREATE TABLE material (
    material_id    VARCHAR(20)   NOT NULL,
    material_name  VARCHAR(80)   NOT NULL,
    description    VARCHAR(255),
    base_unit      VARCHAR(10)   NOT NULL,
    standard_price DECIMAL(15,2),
    weight         DECIMAL(15,3),
    volume         DECIMAL(15,3),
    search_term    VARCHAR(100),
    CONSTRAINT pk_material PRIMARY KEY (material_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_mat_name ON material (material_name);
```

---

## 第3章 逐表设计要点与业务规则

### 3.1 business_partner（业务伙伴主记录）

| 项 | 内容 |
| --- | --- |
| 主键 | bp_id（VARCHAR(20)） |
| 外键 | 无（本表是主数据根表） |
| 索引 | idx_bp_name(bp_name)、idx_bp_region(country, city)、idx_bp_status(status)、idx_bp_changed(last_changed_time) |

关键业务规则：

1. **编号自动生成**：原型 4.2 中 Business Partner No. 字段只读、显示 "Auto-generated"，保存后由系统分配。应用层需实现编号生成（建议规则：前缀 + 序列，如 `C0001`，长度 ≤ 20），数据库侧无自增列。
2. **状态管理**：status 默认 `ACTIVE`；冻结客户通过 `status + block_reason` 表达，**不做物理删除**（全库通则：单据与主数据均不作物理删除，用状态作废）。
3. **审计时间戳**：created_time 默认 CURRENT_TIMESTAMP；last_changed_time 带 ON UPDATE CURRENT_TIMESTAMP，由数据库自动维护，应用层不要显式写入这两个字段。
4. transportation_zone（运输区域）供 D4 线路调度使用，本模块仅维护。

### 3.2 customer_sales_data（客户销售区域数据）

| 项 | 内容 |
| --- | --- |
| 主键 | **复合主键 (bp_id, sales_org, distribution_channel, division)** |
| 外键 | bp_id → business_partner(bp_id)，ON DELETE RESTRICT |
| 索引 | idx_csd_area(sales_org, distribution_channel, division)、idx_csd_plant(delivering_plant) |

关键业务规则：

1. 同一客户在每个销售区域下**各有一条**视图数据，与 SAP 客户主记录销售视图一致；写入时按四元组判重，冲突应返回 409 CONFLICT。
2. 注意 PK 最左列是 bp_id，纯按销售区域维度的查询依赖 idx_csd_area 二级索引。
3. account_assignment_group（科目分配组）供 D5 财务过账；customer_pricing_procedure（定价过程）供 D3 定价——本模块只负责维护字段值，不实现其下游逻辑。

### 3.3 customer_finance_data（客户公司代码财务数据）

| 项 | 内容 |
| --- | --- |
| 主键 | **复合主键 (bp_id, company_code)** |
| 外键 | bp_id → business_partner(bp_id)，ON DELETE RESTRICT |
| 索引 | idx_cfd_company(company_code)、idx_cfd_recon(reconciliation_account) |

关键业务规则：

1. 同一客户在每个公司代码下各有一条财务视图。
2. **设计假设（需在测试记录中注明）**：ER 原图本表主键栏写了两行 company_code，按 SAP KNB1 惯例裁定为 (bp_id, company_code) 复合主键。
3. 银行信息（iban、bank_key、bank_account）与支付卡信息（card_number 等）为敏感字段，接口返回时应考虑脱敏（原型未强制，建议至少对 card_number 脱敏）。

### 3.4 contact（联系人）

| 项 | 内容 |
| --- | --- |
| 主键 | contact_id（VARCHAR(20)） |
| 外键 | bp_id → business_partner(bp_id)，ON DELETE RESTRICT（一个客户 1 : n 个联系人） |
| 索引 | idx_contact_bp(bp_id)、idx_contact_name(last_name, first_name)、idx_contact_phone(personal_phone) |

关键业务规则：删除一个有联系人的客户会被 RESTRICT 阻断——这是有意设计（防止孤儿联系人），测试中应验证该阻断行为而非绕过它。

### 3.5 bp_relationship（业务伙伴关系）

| 项 | 内容 |
| --- | --- |
| 主键 | relation_id（VARCHAR(20)） |
| 外键 | bp_from → business_partner(bp_id)；bp_to → business_partner(bp_id)，均 RESTRICT |
| 索引 | idx_rel_from(bp_from, relationship_type)、idx_rel_to(bp_to, relationship_type)、idx_rel_valid(valid_from, valid_to) |

关键业务规则：

1. **双外键自引用**：表达伙伴之间的有向关系（如"集团-子公司"）；bp_from 与 bp_to 不允许相同（应用层校验）。
2. relationship_type 的候选值由原型 4.7 的 F4 搜索帮助弹窗选择（如 BBP002 等，Direction 列 `->` 单向、`<->` 双向）；接口层应提供关系类型的枚举/字典。
3. 有效期：valid_from / valid_to 可空，但若同时存在必须满足 valid_to ≥ valid_from（提交校验）。

### 3.6 material（物料主记录）

| 项 | 内容 |
| --- | --- |
| 主键 | material_id（VARCHAR(20)） |
| 外键 | 无 |
| 索引 | idx_mat_name(material_name) |

关键业务规则：

1. material 是全库被引用最多的主数据表（D3/D4/D5 全部行项目表均以 RESTRICT 引用它）。本期这些表不建，但**设计上必须保留这一保护语义**：已发生业务的物料禁止删除，只能停用。
2. 库存数量不在 D2（ATP 可用性走物流/MM 域，见 API 3.2 节说明），不要在本表加库存字段。

---

## 第4章 跨模块引用点及其对实现/测试的影响

本模块虽不实现 D3/D4/D5，但这些域会引用本模块的表，影响接口设计与测试数据准备：

| 外部引用方 | 引用本模块的列 | 影响 |
| --- | --- | --- |
| D3 inquiry / quotation / sales_order | customer_id、sold_to_party、ship_to_party → business_partner | 客户主数据是全流程前置条件；测试任何单据前必须先有 BP 数据 |
| D4 delivery | ship_to_party → business_partner | 同上 |
| D5 invoice / receipt | sold_to_party、payer → business_partner | 同上 |
| D3/D4/D5 全部行项目表 | material_id → material | 物料同理 |
| D3 服务层 | 调用 `GET /partners/{bp_id}/credit-check` | 本模块需提供信用检查接口（见 5.1） |

**测试数据准备顺序（必须遵守）**：business_partner → customer_sales_data / customer_finance_data / contact / bp_relationship → material。删除性测试时顺序相反，且应验证 RESTRICT 阻断。

---

## 第5章 API 契约（摘自接口规范 3.1 / 3.2 节）

### 5.1 D1 客户主数据接口

Base：`/api/v1/master`。统一响应、幂等、错误码等全局约定见第 6 章。

| 方法 | 路径 | 说明 | 幂等 |
| --- | --- | --- | --- |
| GET | /partners | 分页检索伙伴 | — |
| GET | /partners/{bp_id} | 伙伴详情 | — |
| POST | /partners | 新建伙伴 | 强制 |
| PATCH | /partners/{bp_id} | 更新/冻结 | — |
| GET | /partners/{bp_id}/sales-views | 销售视图列表 | — |
| PUT | /partners/{bp_id}/sales-views | 创建或更新销售视图 | 强制 |
| GET | /partners/{bp_id}/finance-views | 财务视图列表 | — |
| PUT | /partners/{bp_id}/finance-views | 创建或更新财务视图 | 强制 |
| GET | /partners/{bp_id}/contacts | 联系人列表 | — |
| POST | /partners/{bp_id}/contacts | 新建联系人 | 强制 |
| GET | /partners/{bp_id}/relationships | BP 关系 | — |
| POST | /relationships | 建立 BP 关系 | 强制 |
| GET | /partners/{bp_id}/credit-check | 信用检查（供 D3 调用） | — |

创建伙伴请求示例：

```json
{
  "bp_type": "ORG",
  "bp_role": "SOLD_TO",
  "bp_name": "华东示例科技有限公司",
  "country": "CN",
  "city": "Shanghai",
  "street": "Nanjing Rd",
  "telephone": "021-88886666",
  "email": "sales@example.com",
  "status": "ACTIVE",
  "search_term": "HDKJ"
}
```

销售视图复合键：bp_id + sales_org + distribution_channel + division；另含 currency、price_group、delivering_plant、incoterms、max_partial_deliveries 等。

D1 典型错误码：`MDM_PARTNER_NOT_FOUND`、`MDM_PARTNER_BLOCKED`、`VALIDATION_ERROR`。

### 5.2 D2 物料主数据接口

Base：`/api/v1/master`。

| 方法 | 路径 | 说明 | 幂等 |
| --- | --- | --- | --- |
| GET | /materials | 列表/模糊检索 | — |
| GET | /materials/{material_id} | 详情 | — |
| POST | /materials | 新建（或 MM 同步写入） | 强制 |
| PATCH | /materials/{material_id} | 更新 | — |

请求/响应主字段示例：

```json
{
  "material_id": "M0001",
  "material_name": "Notebook 14inch",
  "description": "商务笔记本",
  "base_unit": "PC",
  "standard_price": 1500.00,
  "weight": 1.250,
  "volume": 0.005,
  "search_term": "NB14"
}
```

D2 典型错误码：`MDM_MATERIAL_NOT_FOUND`、`VALIDATION_ERROR`。

---

## 第6章 全局接口约定（测试必须覆盖）

1. **统一响应**：所有接口返回 `{success, trace_id, timestamp, code, message, data, errors}` 信封；列表 data 为 `{items, pagination{page, page_size, total, total_pages}}`，page 从 1 起，page_size 默认 20、最大 100。
2. **幂等**：创建类 POST 强制请求头 `X-Idempotency-Key`——同键同体返回首次结果，同键异体返回 `IDEMPOTENCY_KEY_REUSED`（409）。
3. **字段命名**：snake_case；未知值用 null，不用空串表示空金额/日期。
4. **数据类型**：日期 `YYYY-MM-DD`；日期时间 ISO 8601 带时区（默认 +08:00）；金额 number 两位小数；数量最多三位小数；币种 ISO 4217；业务单号 string 长度 ≤ 20。
5. **HTTP 方法语义**：GET 查询 / POST 创建或过程动作 / PATCH 部分更新 / DELETE 禁用（用状态作废）。
6. **通用错误码**：OK(200)、CREATED(201)、VALIDATION_ERROR(400)、UNAUTHORIZED(401)、FORBIDDEN(403)、NOT_FOUND(404)、CONFLICT(409)、INTERNAL_ERROR(500)。

---

## 第7章 前端原型对后端的约束

来自原型报告 4.2 / 4.7 / 5.1 节，实现接口与校验逻辑时必须满足：

1. **创建业务伙伴表单**（4.2）：顶部三字段为 Business Partner No.（Auto-generated 只读）、Grouping、BP Role；Tab 含 Address / Identification / Control Data / Payment Transactions / Status 等。Address Tab 字段块：Basic Information（Salutation、Last Name、First Name、Search Term）、Standard Address（Street/House No.、Country/Region、City、Postal Code*、Region）、PO Box Address、Communication（Phone、Email、Fax、Website）。
2. **邮编实时校验**（4.2）：Postal Code 输入时实时格式校验（前端三色指示条）——后端应提供格式校验或在保存时强校验，错误文案格式为「字段名称 + 具体错误」。
3. **三级校验**（5.1）：失焦校验（仅修改后触发；唯一性等异步校验需 500ms 防抖）、提交校验（必填 + 跨字段逻辑，如 valid_to ≥ valid_from）、错误汇总定位。
4. **F4 弹窗**（4.7）：relationship_type 通过搜索帮助选择，单选，条目带 RelCat / Direction / Description；后端需支持按名称模糊检索关系类型字典。
5. **必填标识**：带红色星号字段为必填（当前明确：Postal Code）。

---

## 第8章 测试任务清单（交给 Codex 执行）

### 8.1 数据库层验证

| # | 测试项 | 预期 |
| --- | --- | --- |
| T1 | 执行建库脚本 | 6 张表全部创建成功，InnoDB / utf8mb4 |
| T2 | 复合主键冲突：重复写入同一 (bp_id, sales_org, distribution_channel, division) | 主键冲突报错，接口层映射为 409 |
| T3 | 外键存在性：向 customer_sales_data 写入不存在的 bp_id | FK 拒绝 |
| T4 | RESTRICT 阻断：删除已有 contact / 视图数据的 business_partner | 删除被拒（1451 错误），验证是有意设计 |
| T5 | bp_relationship 自引用：bp_from = bp_to | 应用层校验拒绝 |
| T6 | 时间戳：INSERT 后 created_time 自动写入；UPDATE 任意字段后 last_changed_time 自动变化 | 自动维护，无需应用层赋值 |
| T7 | 索引存在性：SHOW INDEX 核对第 2 章脚本中的全部二级索引 | 全部存在 |

### 8.2 API 层验证

| # | 测试项 | 预期 |
| --- | --- | --- |
| A1 | POST /partners 缺 X-Idempotency-Key | 400 |
| A2 | 同幂等键 + 同请求体重发 | 返回首次结果，不产生重复记录 |
| A3 | 同幂等键 + 不同请求体 | 409 IDEMPOTENCY_KEY_REUSED |
| A4 | POST /partners 成功 | 201，响应信封完整，bp_id 由系统分配 |
| A5 | GET /partners 分页（page/page_size 边界：page_size=101） | 截断至 100 或 400 |
| A6 | PUT sales-views 重复创建同一四元组 | 幂等更新或 409，行为需与规范一致 |
| A7 | PATCH /partners/{bp_id} 冻结（status + block_reason） | 生效；后续 D3 引用该客户应触发 MDM_PARTNER_BLOCKED（本期 mock 验证） |
| A8 | GET /partners/{bp_id}/credit-check | 返回结构符合 D3 调用约定 |
| A9 | 错误响应格式 | 统一信封，errors 数组含字段级错误 |
| A10 | material CRUD + 模糊检索（material_name / search_term） | 正常 |

### 8.3 数据准备顺序

测试前置数据按此顺序构造：business_partner → 各从表（sales/finance/contact/relationship）→ material；清理时逆序，或利用 T4 验证 RESTRICT 后再按依赖序删除。

---

## 第9章 数据类型规范速查

| 用途 | 类型 | 说明 |
| --- | --- | --- |
| 单号 / 编号 | VARCHAR(20) | 业务凭证号，统一长度便于索引 |
| 金额 | DECIMAL(15,2) | 精确小数，禁止 FLOAT |
| 数量 / 重量 / 体积 | DECIMAL(15,3) | 三位小数计量 |
| 日期 | DATE | 生日、有效期等 |
| 时间戳 | DATETIME | 部分带数据库自动默认值 |
| 币种 / 国家 | CHAR(3) / CHAR(2) | ISO 4217 / ISO 3166 |
| 备注 / 检索词 | VARCHAR(255) / VARCHAR(100) | 各表统一冗余 |

---

## 第10章 已知设计决策与待确认事项

1. **customer_finance_data 主键**：ER 原图主键栏重复写了 company_code，已按 SAP KNB1 惯例裁定为 (bp_id, company_code)——若课程评审提出异议，以此条为决策记录。
2. **bp_id 编号生成规则**：原型要求 Auto-generated，但具体编号规则（前缀、长度、是否按 bp_role 分段）未在报告中定义，实现前需与小组确认；建议先实现简单的全局序列（C + 5 位序号）。
3. **D4 表在同一定稿脚本中**：`sap_sd_d124.sql` 还含 delivery / delivery_item / goods_issue（属于 Delivery Management 模块，本期不测试）。其中 delivery_item.so_item_id 为指向 D3 的逻辑引用列（无 FK），不影响本模块。
4. **脱敏**：card_number、iban 等敏感字段的接口脱敏级别未在原型中强制，建议实现时至少对卡号做掩码，并在测试中验证。
5. **Grouping 字段**：原型 4.2 顶部有 Grouping 字段，business_partner 表中与之对应的是 permission_group / data_source 区域，映射关系需在联调时与前端确认。
