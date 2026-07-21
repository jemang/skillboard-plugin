---
name: database-design-doc
description: >-
  Generate or update a database-design.md file that documents an application's
  database — table-by-table column design, primary/foreign keys, indexes, a
  Mermaid ER diagram showing how every table connects, and a written summary
  explaining the schema. Use this WHENEVER the user asks to document the
  database, generate or update database-design.md, draw an ER / entity-relationship
  diagram, map how tables relate, summarize the DB schema, or wants current
  documentation of the data model. Works for Laravel (migrations + Eloquent
  models) and Rails (schema.rb + ActiveRecord models), and degrades gracefully
  for other SQL stacks. Trigger even when the user is terse — "document my db",
  "update the schema doc", "show how my tables connect" all count.
---

# Database Design Doc

Produce a single self-contained `database-design.md` that a new engineer can
read to understand the whole data model: every table's columns, how tables
relate (with a visual ER diagram), and prose explaining *why* the schema looks
the way it does.

The database is the source of truth. **Derive the doc from the code, never from
memory or from a previous version of the doc.** Schemas drift; the whole point
of this skill is to reflect what the code says *right now*.

## Workflow

1. Pick the app to document.
2. Detect the stack and locate the schema sources.
3. Extract tables, columns, keys, indexes, and relationships.
4. Build the Mermaid ER diagram.
5. Write (or update) `database-design.md` in that app's root.
6. Run the quality checklist before you call it done.

---

## Step 1 — Pick the app

The doc lives in the app's own root folder, so first decide *which* app.

- List candidate app directories under the working directory. An "app" is any
  directory that has a framework signature:
  - **Laravel**: a `composer.json` requiring `laravel/framework`, plus
    `database/migrations/`.
  - **Rails**: a `Gemfile` with `rails`, plus `config/application.rb` and
    `db/schema.rb`.
  - Other SQL stacks: a `migrations/`, `schema.sql`, `prisma/schema.prisma`,
    `models.py`, etc.
- **If exactly one app is found**, use it (briefly state which one).
- **If more than one app is found**, ask the user which one to document — do not
  guess. Show the list. The chosen app's root is where `database-design.md` goes.
- **If none is found** in subdirectories, check whether the current directory
  itself is the app.

---

## Step 2 — Detect the stack and find the schema

Read the *authoritative* schema and the *relationship* definitions separately —
columns and relationships live in different places.

### Laravel
- **Columns / indexes / FKs**: every file in `database/migrations/*.php`. Read
  the `Schema::create` and `Schema::table` blueprints. Watch for:
  - `$table->id()` → `bigint id` PK.
  - `$table->foreignId('user_id')->constrained()->cascadeOnDelete()` →
    `user_id` FK to `users.id`, `ON DELETE CASCADE`.
  - column modifiers: `->nullable()`, `->default(...)`, `->unique()`.
  - `$table->index([...])`, `$table->unique([...])`, `$table->timestamps()`
    (adds `created_at`, `updated_at`).
  - Later migrations may `Schema::table(...)` to alter an existing table — fold
    those changes into the final picture.
- **Relationships**: `app/Models/*.php`. Read the relation methods —
  `belongsTo`, `hasMany`, `hasOne`, `belongsToMany`, `morphTo`, `morphMany`.
  Also note `$casts` (e.g. `boolean`, `datetime`, `hashed`), `#[Fillable(...)]`,
  and `#[Hidden(...)]` for column notes.
- **Driver**: `DB_CONNECTION` in `.env`, falling back to `config/database.php`.

### Rails
- **Columns / indexes / FKs**: `db/schema.rb` is the single source of truth —
  it's auto-generated and authoritative. Each `create_table` lists columns
  (`t.string`, `t.integer`, `t.datetime`, `t.boolean`, `t.text`, `t.json`...),
  `null:` / `default:` options, and `t.index`. The `add_foreign_key` lines at
  the bottom define FKs. Note: Rails adds an implicit `bigint id` PK per table
  unless told otherwise, and `t.timestamps` → `created_at` + `updated_at`.
- **Relationships**: `app/models/*.rb`. Read `belongs_to`, `has_many`,
  `has_one`, `has_and_belongs_to_many`, `has_many ..., through:`, and
  polymorphic `as:` / `class_name:` options. Also capture `enum`, `validates`,
  and `has_rich_text` / `has_one_attached` (these imply extra backing tables
  like `action_text_rich_texts` / `active_storage_*`).
- Read the version line in `schema.rb` for the schema version, and check
  `config/database.yml` for the adapter.

### Other stacks
Find the schema however the framework defines it (`schema.sql`, Prisma schema,
SQLAlchemy/Django models, Sequelize/TypeORM entities). The output format below
is stack-agnostic — only the extraction differs.

---

## Step 3 — Extract the model

For every table collect: name, purpose (infer from columns + model), columns
(name, type, nullable, default, key role), indexes, and relationships.

**Classify each table** so the doc stays readable:
- **Domain tables** — the app's own business data (e.g. `users`, `notes`,
  `credentials`, `checklist_items`). These are the stars of the ER diagram.
- **Framework / system tables** — plumbing the framework generates and the
  reader rarely cares about internally: `cache`, `jobs`, `failed_jobs`,
  `password_reset_tokens`, `active_storage_*`, `action_text_rich_texts`,
  `noticed_*`, `audits`, `*_schema_migrations`, etc. Still document them, but in
  their own subsection. You may keep most of them out of the main ER diagram to
  avoid clutter — if you do, say so in one line.

Reconcile the two sources: the migration/schema gives the FK columns; the model
gives the *semantics* (cardinality, cascade, naming). A `user_id` column plus a
`belongs_to :user` / `hasMany(Note::class)` pair is one relationship — describe
it once, from both ends.

### Group domain tables into modules
Grouping is what keeps a large schema readable, so do it deliberately rather
than alphabetically. Apply these signals in order and stop when a table lands in
a clear group:

1. **Foreign-key clusters.** Tables joined by FKs usually belong together — walk
   the FK graph and treat each connected cluster as a candidate domain (e.g.
   `orders` → `order_items` → `shipments`).
2. **Name prefixes / shared roots.** `billing_*`, `oauth_*`, `cms_*` are a
   grouping the schema author already made explicit — honor it.
3. **Code module / namespace.** Model directory or namespace
   (`App\Models\Billing\…`, Rails engines/modules) is a strong domain signal.
4. **Hub tables don't absorb everything.** A central table nearly everything FKs
   into (often `users` / `accounts` / `tenants`) would, by FK clustering alone,
   swallow the whole schema. Give it its own small "Core" / "Accounts" group and
   let the spoke domains stand on their own.
5. **Name each group by business capability**, not by tech — "Billing",
   "Content", "Notifications"; never "tables with a status column".
6. Aim for ~4–10 tables per group. Split a group that grows past that; fold a
   lonely table into its nearest neighbor or a small "Misc" group.

Order groups core-first (the hub domain), then the domains that depend on it.
Each group becomes one `###` section — and, for a large schema, one detailed
`erDiagram` placed under that section's heading. For a small schema the groups
are still useful as section headings even though one combined diagram suffices.
If a knowledge-graph / architecture MCP is available (it can return module
"communities"), use it to seed groups, then refine with the signals above.

---

## Step 4 — Build the Mermaid ER diagram

Use a `mermaid` `erDiagram` block so it renders in GitHub and VSCode preview.

### Cardinality symbols (the bit that's easy to get wrong)
Each side of a relationship has a symbol; read the symbol *next to* its entity.

| Symbol | Meaning (for the entity it touches) |
|--------|-------------------------------------|
| `||`   | exactly one |
| `o|`   | zero or one |
| `}o`   | zero or many |
| `}|`   | one or many |

Line form: `LEFT  <left-sym>--<right-sym>  RIGHT : "label"`.

### Mapping associations → cardinality
- `belongsTo` / `belongs_to` on the child **and** `hasMany` / `has_many` on the
  parent → `PARENT ||--o{ CHILD : "has many"`. (Use `}|` instead of `o{` only if
  the FK is `NOT NULL` *and* the domain guarantees at least one — usually `o{`
  is right.)
- `hasOne` / `has_one` → `PARENT ||--o| CHILD : "has one"`.
- `belongsToMany` / `has_and_belongs_to_many` / `has_many through:` →
  many-to-many: draw both sides to the join table (`A ||--o{ JOIN`,
  `B ||--o{ JOIN`) when the join table is its own entity, or
  `A }o--o{ B : "label"` if you're abstracting the join away.
- **Polymorphic** (`morphTo`, Rails `as: :recipient`) → one table points at many
  others via `*_type` + `*_id`. Mermaid can't express this natively; draw a line
  to each concrete type you can identify and add a `: "polymorphic"` label, or
  note it in prose if the targets are open-ended.

### Entity blocks
List each table's columns with type and key tag **inside the diagram**. Tags:
`PK`, `FK`, `UK` (unique). Put nullability / default / encryption etc. in the
trailing quoted note. The ER diagram is the **single place columns are listed**
— the table sections below must NOT repeat them as markdown column tables.

```
erDiagram
    USERS ||--o{ NOTES : "has many"
    USERS ||--o{ CREDENTIALS : "has many"
    NOTES ||--o{ CHECKLIST_ITEMS : "has many"

    USERS {
        bigint id PK
        string email_address UK
        string password_digest
        integer role "default 0"
    }
    NOTES {
        bigint id PK
        bigint user_id FK
        string title
        boolean pinned "default false"
    }
    CHECKLIST_ITEMS {
        bigint id PK
        bigint note_id FK
        string content
        integer position
    }
```

### Choosing the diagram layout (scale matters)
One giant diagram with every column is unreadable past a dozen tables. Pick the
layout from the schema size — this is what keeps the doc readable on a large DB:

- **Small (≲ 12 domain tables):** a single `erDiagram` with attribute blocks, as
  above.
- **Large / many tables:** lead with an **overview diagram** — entities and
  relationship lines only, *no* attribute blocks — so the whole map fits on one
  screen. Then split tables into domains using the grouping signals in Step 3
  ("Group domain tables into modules") and give each domain its own **detailed
  `erDiagram`** (with attributes) placed next to that domain's table
  descriptions. Aim for ≲ 10 entities per detailed diagram.
- Keep framework / plumbing tables out of the diagrams unless a domain table
  directly references one. A diagram nobody can read helps nobody.

---

## Step 5 — Write `database-design.md`

Write to `<chosen-app-dir>/database-design.md` using this structure exactly:

```markdown
# Database Design — <App Name>

> Generated by the `database-design-doc` skill on <YYYY-MM-DD>.
> Stack: <e.g. Laravel 11 / Rails 8.1> · Driver: <e.g. sqlite> · Source of truth: <schema files>.

## Overview

<1–2 short paragraphs, plain language: what this database stores, the central
entity everything hangs off (often `users`), and the one or two patterns a
reader truly needs up front (per-user ownership, cascade deletes, etc.). Keep
it tight — no filler.>

## Entity-Relationship Diagram

<Small schema: one erDiagram with attributes. Large schema: an overview diagram
here (entities + relationships only, no attributes), then a detailed diagram per
domain placed under that domain's tables below — see "Choosing the diagram
layout".>

```mermaid
erDiagram
    ...
```

<One line under each diagram noting any tables intentionally left out and why.>

## Tables

Group tables by domain with a `###` heading per group (e.g. `### Accounts`,
`### Content`), using the grouping signals from Step 3. Order groups core-first.
Within a group, one **compact** entry per table — no column tables; the columns
already live in the ER diagram. Drop any bullet that has nothing to say, so
small tables stay one or two lines.

### <Domain group>

<For a large schema, place this domain's detailed `erDiagram` here.>

#### <table_name> — <one-line purpose>

- **Keys:** PK `id`; FK `user_id` → `users.id` (cascade on delete).
- **Notable columns:** only ones needing explanation — encrypted, enum /
  discriminator, JSON, polymorphic `*_type`/`*_id`, or a nullable column the app
  actually requires. Skip self-evident columns and plain timestamps.
- **Relationships:** belongs to `users`; has many `checklist_items` (from both ends).
- **Indexes:** composite (`user_id`, `pinned`) — and the query it serves.

<repeat per table>

## Framework / System Tables

<One line each — these are framework plumbing (cache, jobs, file storage,
auditing, password resets). Name + purpose + PK is enough; don't list every
column for standard plumbing.>

## Summary

<A few bullets, only what matters — the ownership/tenancy model, any unusual
schema choice, and any concrete rough edge worth flagging (missing index,
nullable FK that probably shouldn't be). No table here. No generic database
advice, no restating the column tables above. If there's nothing notable beyond
what the tables and diagram already show, keep this very short.>

## Manual Notes

<!-- Add notes below this marker. Everything under this heading is preserved
     when the doc is regenerated. -->
```

### Updating an existing doc
If `database-design.md` already exists:
- Regenerate every auto section from the current code — the schema may have
  changed, and stale docs are worse than none.
- **Preserve the `## Manual Notes` section verbatim** (read the old file first,
  carry that block over). That's the one place humans add things the code can't
  tell you.
- It's fine to mention in your reply what changed since the previous version
  (tables/columns/relationships added or removed) if you can tell.

---

## Quality checklist

Before declaring done, verify:

- [ ] Every table from the schema appears in the doc (domain + framework).
- [ ] **No per-column markdown tables** — columns live only in the ER diagram(s);
      the table sections are compact bullets.
- [ ] Each FK is shown (in the diagram's `FK` tag and the table's **Keys** bullet)
      with its on-delete rule.
- [ ] Every relationship is described from both ends and matches the model code.
- [ ] Tables are grouped by business domain (core-first), not alphabetically;
      no group is so big it stops being a "domain".
- [ ] Large schemas use an overview diagram + per-domain detailed diagrams, not
      one unreadable mega-diagram; each diagram stays legible (≲ 10 entities).
- [ ] The Mermaid block is syntactically valid (entity names referenced in
      relationships are also defined as entity blocks; cardinality symbols are
      from the table above).
- [ ] The Overview and Summary are specific to this schema, not boilerplate.
- [ ] If a prior doc existed, its `## Manual Notes` survived.
- [ ] The file was written to the chosen app's root, not the working directory.
```
