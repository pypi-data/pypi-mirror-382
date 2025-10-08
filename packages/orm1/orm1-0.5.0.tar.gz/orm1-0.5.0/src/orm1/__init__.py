import re
import types
import typing
from typing import Collection, Sequence, Type, Self
from contextlib import asynccontextmanager

import asyncpg
import asyncpg.transaction

Entity = object
KeyLike = typing.Union[typing.Hashable, tuple[typing.Hashable, ...]]
Value = typing.Any
ParamMap = dict[typing.Hashable, Value]
TEntity = typing.TypeVar("TEntity", bound=Entity)
Record = dict[str, Value]


class Key(tuple[typing.Hashable]):
    @classmethod
    def from_key_like(cls, key_like: KeyLike) -> "Key":
        if isinstance(key_like, tuple):
            return cls(typing.cast(tuple[typing.Hashable, ...], key_like))
        return cls((key_like,))


class AttributeAccessor(typing.Protocol):
    def get(self, entity: Entity) -> Value: ...
    def set(self, entity: Entity, value: Value): ...


class EntityFactory(typing.Protocol):
    def create(self) -> Entity: ...


class Field(typing.NamedTuple):
    name: str
    column: str
    accessor: AttributeAccessor


class Child(typing.NamedTuple):
    target: type[Entity]
    accessor: AttributeAccessor


class EntityIdentity(typing.NamedTuple):
    type: Type[Entity]
    parental_key: Key
    primary_key: Key


class IdentityMap:
    def __init__(self, data: dict[tuple[type, Key], dict[EntityIdentity, object]] | None = None):
        self._idm = data or {}

    def track(self, identity: EntityIdentity, entity: Entity):
        scope = self._idm.setdefault((identity.type, identity.parental_key), {})
        scope[identity] = entity

    def untrack(self, identity: EntityIdentity):
        self._idm.get((identity.type, identity.parental_key), {}).pop(identity)

    def in_track(self, identity: EntityIdentity):
        scope = self._idm.setdefault((identity.type, identity.parental_key), {})
        return identity in scope

    def get_tracked(self, identity: EntityIdentity):
        scope = self._idm.setdefault((identity.type, identity.parental_key), {})
        return scope.get(identity)

    def get_tracked_children(self, type: Type[Entity], parental_key: Key):
        return set(self._idm.get((type, parental_key), {}).keys())

    def copy(self):
        return IdentityMap({k: dict(v) for k, v in self._idm.items()})


class EntityMapping(typing.NamedTuple):
    entity_type: Type[Entity]
    entity_factory: EntityFactory
    schema: str
    table: str
    fields: dict[str, Field]
    children: dict[str, Child]
    primary_key: list[str]
    parental_key: list[str]
    insertable: list[str]
    updatable: list[str]

    def get_fields(self):
        return self.fields.values()

    def get_insertable_fields(self):
        return [self.fields[fn] for fn in self.insertable]

    def get_updatable_fields(self):
        return [self.fields[fn] for fn in self.updatable]

    def get_primary_fields(self):
        return [self.fields[fn] for fn in self.primary_key]

    def get_parental_fields(self):
        return [self.fields[fn] for fn in self.parental_key]

    def primary_key_from_entity(self, entity: Entity) -> Key:
        return Key(self.fields[fn].accessor.get(entity) for fn in self.primary_key)

    def parental_key_from_entity(self, entity: Entity) -> Key:
        return Key(self.fields[fn].accessor.get(entity) for fn in self.parental_key)

    def identify_entity(self, entity: Entity) -> EntityIdentity:
        return EntityIdentity(
            type=self.entity_type,
            parental_key=self.parental_key_from_entity(entity),
            primary_key=self.primary_key_from_entity(entity),
        )

    def identify_record(self, rec: Record) -> EntityIdentity:
        return EntityIdentity(
            type=self.entity_type,
            parental_key=Key(rec[f] for f in self.parental_key),
            primary_key=Key(rec[f] for f in self.primary_key),
        )

    def write_to_entity(self, entity: Entity, rec: Record):
        for fn in rec:
            self.fields[fn].accessor.set(entity, rec[fn])


sql_n = typing.NamedTuple("sql_n", [("part", str)])
sql_qn = typing.NamedTuple("sql_qn", [("part1", str), ("part2", str)])
sql_text = typing.NamedTuple("sql_text", [("text", str)])
sql_param = typing.NamedTuple("sql_param", [("id", typing.Hashable)])
sql_all = typing.NamedTuple("sql_all", [("els", list["SQL"])])
sql_any = typing.NamedTuple("sql_any", [("els", list["SQL"])])
sql_eq = typing.NamedTuple("sql_eq", [("left", "SQL"), ("right", "SQL")])
sql_lt = typing.NamedTuple("sql_lt", [("left", "SQL"), ("right", "SQL")])
sql_gt = typing.NamedTuple("sql_gt", [("left", "SQL"), ("right", "SQL")])
sql_is_null = typing.NamedTuple("sql_is_null", [("operand", "SQL")])
sql_is_not_null = typing.NamedTuple("sql_is_not_null", [("operand", "SQL")])
sql_fragment = typing.NamedTuple("sql_fragment", [("els", list["SQL"])])

SQL = sql_n | sql_qn | sql_text | sql_param | sql_all | sql_any | sql_eq | sql_lt | sql_gt | sql_is_null | sql_is_not_null | sql_fragment


class SQLSelect(typing.NamedTuple):
    select: list[str]
    from_schema: str
    from_table: str
    key_columns: list[str]


class SQLInsert(typing.NamedTuple):
    into_schema: str
    into_table: str
    insert: list[str]
    returning: list[str]


class SQLUpdate(typing.NamedTuple):
    schema: str
    table: str
    sets: list[str]
    where: list[str]
    returning: list[str]


class SQLDelete(typing.NamedTuple):
    from_schema: str
    from_table: str
    key_columns: list[str]


class SQLQuery(typing.NamedTuple):
    class Join(typing.NamedTuple):
        type: typing.Literal["JOIN", "LEFT JOIN"]
        table: SQL
        alias: SQL
        on: SQL

    class OrderBy(typing.NamedTuple):
        expr: SQL
        ascending: bool = True
        nulls_last: bool = True

    select: Collection[SQL]
    from_table: SQL
    from_alias: SQL
    joins: Collection[Join] = ()
    where: SQL | None = None
    order_bys: Collection[OrderBy] = ()
    group_by: Collection[SQL] = ()
    having: SQL | None = None
    limit: SQL | None = None
    offset: SQL | None = None


Row = tuple[Value, ...]


class SessionBackend(typing.Protocol):
    async def select(self, stmt: SQLSelect, values: list[ParamMap]) -> list[Row]: ...
    async def insert(self, stmt: SQLInsert, values: list[ParamMap]) -> list[Row]: ...
    async def update(self, stmt: SQLUpdate, values: list[ParamMap]) -> list[Row]: ...
    async def delete(self, stmt: SQLDelete, values: list[ParamMap]): ...
    async def fetch_query(self, stmt: SQLQuery, param_map: ParamMap) -> list[Row]: ...
    async def count_query(self, stmt: SQLQuery, param_map: ParamMap) -> int: ...
    async def fetch_raw(self, raw: SQL, param_map: ParamMap) -> list[Row]: ...
    async def begin(self): ...
    async def commit(self): ...
    async def rollback(self): ...
    async def savepoint(self, name: str): ...
    async def release(self, name: str): ...
    async def rollback_to(self, name: str): ...


class Session:
    def __init__(self, backend: SessionBackend, mappings: Collection[EntityMapping]):
        self._backend = backend
        self._mappings = {mapping.entity_type: mapping for mapping in mappings}
        self._idm = IdentityMap()
        self._tx_depth = 0

    async def get(self, entity_type: Type[TEntity], id: KeyLike) -> TEntity | None:
        return (await self.batch_get(entity_type, (id,)))[0]

    async def save(self, entity: Entity) -> None:
        await self.batch_save(type(entity), entity)

    async def delete(self, entity: Entity) -> None:
        await self.batch_delete(type(entity), entity)

    async def batch_get(self, entity_type: Type[TEntity], ids: typing.Iterable[KeyLike]) -> list[TEntity | None]:
        mapping = self.get_mapping(entity_type)
        primary_keys = [Key.from_key_like(id) for id in ids]
        entity_map = await self._get(
            mapping=mapping,
            key_cols=[f.column for f in mapping.get_primary_fields()],
            keys=primary_keys,
        )
        return typing.cast(list[TEntity | None], [entity_map.get(pk) for pk in primary_keys])

    async def batch_save(self, entity_type: Type[TEntity], *entities: TEntity) -> None:
        mapping = self.get_mapping(entity_type)
        await self._save(mapping, list(entities))

    async def batch_delete(self, entity_type: Type[TEntity], *entities: TEntity) -> None:
        mapping = self.get_mapping(entity_type)
        if to_delete := [e for e in entities if self._idm.in_track(mapping.identify_entity(e))]:
            await self._delete(mapping, to_delete)

    async def _get(self, mapping: EntityMapping, key_cols: list[str], keys: list[Key]) -> dict[Key, Entity]:
        if keys:
            select_stmt = SQLSelect(
                from_schema=mapping.schema,
                from_table=mapping.table,
                select=[f.column for f in mapping.get_fields()],
                key_columns=key_cols,
            )
            values = [ParamMap(zip(key_cols, key)) for key in keys]
            rows = await self._backend.select(select_stmt, values)
            records = [{f.name: val for f, val in zip(mapping.get_fields(), row)} for row in rows]
        else:
            records = []

        ent_map: dict[Key, Entity] = {}
        for rec in records:
            eid = mapping.identify_record(rec)
            entity = self._idm.get_tracked(eid) or mapping.entity_factory.create()
            mapping.write_to_entity(entity, rec)
            self._idm.track(eid, entity)
            ent_map[eid.primary_key] = entity

        for child in mapping.children.values():
            child_mapping = self.get_mapping(child.target)
            child_ent_map = await self._get(
                mapping=child_mapping,
                key_cols=[f.column for f in child_mapping.get_parental_fields()],
                keys=list(ent_map.keys()),
            )

            child_groups = dict[Key, list[Entity]]()
            for child_entity in child_ent_map.values():
                parental_key = child_mapping.parental_key_from_entity(child_entity)
                child_groups.setdefault(parental_key, []).append(child_entity)

            for primary_key, entity in ent_map.items():
                child.accessor.set(entity, child_groups.get(primary_key, ()))

        return ent_map

    async def _save(self, mapping: EntityMapping, entities: list[Entity]) -> None:
        if updatable_fields := mapping.get_updatable_fields():
            if to_update := [e for e in entities if self._idm.in_track(mapping.identify_entity(e))]:
                update_stmt = SQLUpdate(
                    schema=mapping.schema,
                    table=mapping.table,
                    sets=[f.column for f in updatable_fields],
                    returning=[f.column for f in mapping.get_fields()],
                    where=[f.column for f in mapping.get_primary_fields()],
                )
                param_fields = [*updatable_fields, *mapping.get_primary_fields()]
                values = [ParamMap({f.column: f.accessor.get(e) for f in param_fields}) for e in to_update]
                rows = await self._backend.update(update_stmt, values)

                for e, row in zip(to_update, rows):
                    rec = {f.name: v for f, v in zip(mapping.get_fields(), row)}
                    mapping.write_to_entity(e, rec)
                    self._idm.track(mapping.identify_entity(e), e)

        if insertable_fields := mapping.get_insertable_fields():
            if to_insert := [e for e in entities if not self._idm.in_track(mapping.identify_entity(e))]:
                insert_stmt = SQLInsert(
                    into_schema=mapping.schema,
                    into_table=mapping.table,
                    insert=[f.column for f in insertable_fields],
                    returning=[f.column for f in mapping.get_fields()],
                )
                param_fields = insertable_fields
                values = [ParamMap({f.column: f.accessor.get(e) for f in param_fields}) for e in to_insert]
                rows = await self._backend.insert(insert_stmt, values)

                for e, row in zip(to_insert, rows):
                    rec = {f.name: v for f, v in zip(mapping.get_fields(), row)}
                    mapping.write_to_entity(e, rec)
                    self._idm.track(mapping.identify_entity(e), e)

        for child in mapping.children.values():
            child_mapping = self.get_mapping(child.target)
            to_delete = list[Entity]()
            to_save = list[Entity]()
            for entity in entities:
                primary_key = mapping.primary_key_from_entity(entity)
                child_entities = child.accessor.get(entity)

                parental_key = dict(zip(child_mapping.parental_key, primary_key))
                for child_entity in child_entities:
                    child_mapping.write_to_entity(child_entity, parental_key)

                current_ids = {child_mapping.identify_entity(e) for e in child_entities}
                previous_ids = self._idm.get_tracked_children(child_mapping.entity_type, primary_key)

                for id in previous_ids - current_ids:
                    to_delete.append(self._idm.get_tracked(id))

                for child_entity in child_entities:
                    to_save.append(child_entity)

            if to_delete:
                await self._delete(child_mapping, to_delete)
            if to_save:
                await self._save(child_mapping, to_save)

    async def _delete(self, mapping: EntityMapping, entities: Collection[Entity]) -> None:
        for child in mapping.children.values():
            child_mapping = self.get_mapping(child.target)
            to_delete = list[Entity]()

            for e in entities:
                primary_key = mapping.primary_key_from_entity(e)
                for child_eid in self._idm.get_tracked_children(child_mapping.entity_type, primary_key):
                    to_delete.append(self._idm.get_tracked(child_eid))

            if to_delete:
                await self._delete(child_mapping, to_delete)

        stmt = SQLDelete(
            from_schema=mapping.schema,
            from_table=mapping.table,
            key_columns=[f.column for f in mapping.get_primary_fields()],
        )
        values = [ParamMap({f.column: f.accessor.get(e) for f in mapping.get_primary_fields()}) for e in entities]
        await self._backend.delete(stmt, values)

        for entity in entities:
            self._idm.untrack(mapping.identify_entity(entity))

    def query(self, entity_type: Type[TEntity], alias: str) -> "SessionEntityQuery[TEntity]":
        return SessionEntityQuery[TEntity](self, self.get_mapping(entity_type), alias)

    def raw(self, query: str, **params: Value) -> "SessionRawQuery":
        return SessionRawQuery(self, query, params)

    @asynccontextmanager
    async def tx(self) -> typing.AsyncGenerator[None, None]:
        await self._start_tx()
        prev_idm = self._idm.copy()
        try:
            yield
            await self._end_tx()
        except Exception:
            await self._rollback_tx()
            self._idm = prev_idm
            raise

    async def _start_tx(self) -> None:
        if self._tx_depth == 0:
            await self._backend.begin()
        else:
            await self._backend.savepoint(f"tx_{self._tx_depth}")
        self._tx_depth += 1

    async def _end_tx(self) -> None:
        self._tx_depth -= 1
        if self._tx_depth == 0:
            await self._backend.commit()
        else:
            await self._backend.release(f"tx_{self._tx_depth}")

    async def _rollback_tx(self) -> None:
        self._tx_depth -= 1
        if self._tx_depth == 0:
            await self._backend.rollback()
        else:
            await self._backend.rollback_to(f"tx_{self._tx_depth}")

    async def fetch_session_entity_query(
        self, query: "SessionEntityQuery[TEntity]", limit: int | None, offset: int | None
    ) -> list[TEntity]:
        params = ParamMap(query.params)
        limit_ref = query.ctx.new_param_id()
        offset_ref = query.ctx.new_param_id()
        params.update({limit_ref: limit, offset_ref: offset})
        select_stmt = SQLQuery(
            select=[sql_qn(query.alias, f.column) for f in query.mapping.get_primary_fields()],
            from_table=sql_qn(query.mapping.schema, query.mapping.table),
            from_alias=sql_n(query.alias),
            joins=query.joins.values(),
            where=sql_all(query.where_conds) if query.where_conds else None,
            group_by=query.group_by_exprs if query.group_by_exprs else (),
            having=sql_all(query.having_conds) if query.having_conds else None,
            order_bys=query.order_by_opts,
            limit=sql_param(limit_ref),
            offset=sql_param(offset_ref),
        )
        rows = await self._backend.fetch_query(select_stmt, params)
        keys = [Key(row) for row in rows]
        entities = await self._get(query.mapping, [f.column for f in query.mapping.get_primary_fields()], keys)
        return [typing.cast(TEntity, e) for e in entities.values()]

    async def count_session_entity_query(self, query: "SessionEntityQuery[TEntity]") -> int:
        select_stmt = SQLQuery(
            select=[sql_qn(query.alias, f.column) for f in query.mapping.get_primary_fields()],
            from_table=sql_qn(query.mapping.schema, query.mapping.table),
            from_alias=sql_n(query.alias),
            joins=query.joins.values(),
            where=sql_all(query.where_conds) if query.where_conds else None,
            group_by=query.group_by_exprs if query.group_by_exprs else (),
            having=sql_all(query.having_conds) if query.having_conds else None,
        )
        return await self._backend.count_query(select_stmt, query.params)

    class PageOpts(typing.NamedTuple):
        first: int | None
        after: KeyLike | None
        last: int | None
        before: KeyLike | None
        offset: int | None

    class Page(typing.NamedTuple):
        cursors: list[KeyLike]
        has_previous_page: bool
        has_next_page: bool

    async def paginate_session_entity_query(self, query: "SessionEntityQuery[TEntity]", opts: PageOpts):
        first, after, last, before, offset = opts

        after = Key.from_key_like(after) if after else None
        before = Key.from_key_like(before) if before else None

        order_by = [*query.order_by_opts]
        for f in query.mapping.get_primary_fields():
            order_by.append(SQLQuery.OrderBy(sql_qn(query.alias, f.column)))
        if last is not None:
            order_by = [SQLQuery.OrderBy(o.expr, not o.ascending, not o.nulls_last) for o in order_by]

        params = ParamMap(query.params)

        cursor_filters = []
        if after_row := await self._fetch_cursor_row(query, order_by, after) if after else None:
            after_params = ParamMap((query.ctx.new_param_id(), v) for v in after_row)
            predicate = self._format_cursor_predicate(order_by, after_params, last is None)
            cursor_filters.append(predicate)
            params.update(after_params)
        if before_row := await self._fetch_cursor_row(query, order_by, before) if before else None:
            before_params = ParamMap((query.ctx.new_param_id(), v) for v in before_row)
            predicate = self._format_cursor_predicate(order_by, before_params, last is not None)
            cursor_filters.append(predicate)
            params.update(before_params)

        if query.group_by_exprs:
            having_filters = query.having_conds.copy()
            where_filters = query.where_conds
        else:
            having_filters = query.having_conds
            where_filters = query.where_conds.copy()

        if query.group_by_exprs:
            having_filters.extend(cursor_filters)
        else:
            where_filters.extend(cursor_filters)

        limit = first if last is None else last
        limit_ref = query.ctx.new_param_id()
        offset_ref = query.ctx.new_param_id()
        params.update({limit_ref: limit + 1 if limit else None, offset_ref: offset})

        record_fields = query.mapping.get_primary_fields()
        sql_query = SQLQuery(
            select=[sql_qn(query.alias, f.column) for f in record_fields],
            from_table=sql_qn(query.mapping.schema, query.mapping.table),
            from_alias=sql_n(query.alias),
            joins=query.joins.values(),
            where=sql_all(where_filters) if where_filters else None,
            group_by=query.group_by_exprs if query.group_by_exprs else (),
            having=sql_all(having_filters) if having_filters else None,
            order_bys=order_by,
            limit=sql_param(limit_ref),
            offset=sql_param(offset_ref),
        )
        rows = await self._backend.fetch_query(sql_query, params)
        key_rows = rows[:limit]

        if last is None:
            has_previous_page = bool(after_row) or bool(offset)
            has_next_page = len(rows) > limit if limit else False
        else:
            has_previous_page = len(rows) > limit if limit else False
            has_next_page = bool(before_row) or bool(offset)
            key_rows.reverse()

        cursors: list[KeyLike] = [row[0] if len(row) == 1 else tuple(row) for row in key_rows]
        return self.Page(cursors, has_previous_page, has_next_page)

    async def _fetch_cursor_row(self, query: "SessionEntityQuery[TEntity]", order_bys: Sequence[SQLQuery.OrderBy], cursor: Key):
        params = ParamMap(query.params)

        pk_filters = []
        for f, value in zip(query.mapping.get_primary_fields(), cursor):
            param_id = query.ctx.new_param_id()
            params[param_id] = value
            pk_filters.append(sql_eq(sql_qn(query.alias, f.column), sql_param(param_id)))

        if query.group_by_exprs:
            where_filters = query.where_conds
            having_filters = query.having_conds.copy()
            having_filters.extend(pk_filters)
        else:
            where_filters = query.where_conds.copy()
            where_filters.extend(pk_filters)
            having_filters = query.having_conds

        sql_query = SQLQuery(
            select=[o.expr for o in order_bys],
            from_table=sql_qn(query.mapping.schema, query.mapping.table),
            from_alias=sql_n(query.alias),
            joins=query.joins.values(),
            where=sql_all(where_filters) if where_filters else None,
            group_by=query.group_by_exprs if query.group_by_exprs else (),
            having=sql_all(having_filters) if having_filters else None,
        )
        rows = await self._backend.fetch_query(sql_query, params)
        return rows[0] if rows else None

    def _format_cursor_predicate(self, order_bys: list[SQLQuery.OrderBy], params: ParamMap, is_forward: bool):
        param_refs = [sql_param(id) for id in params]
        or_predicates: list[SQL] = []
        for i, _ in enumerate(order_bys):
            and_predicates: list[SQL] = []
            for j, sort in enumerate(order_bys[: i + 1]):
                v = param_refs[j]
                if i != j:
                    comp = sql_eq(v, sort.expr)
                elif sort.ascending == is_forward:
                    comp = sql_lt(v, sort.expr)
                else:
                    comp = sql_gt(v, sort.expr)
                if i != j:
                    null = sql_all([sql_is_null(v), sql_is_null(sort.expr)])
                elif sort.nulls_last == is_forward:
                    null = sql_all([sql_is_not_null(v), sql_is_null(sort.expr)])
                else:
                    null = sql_all([sql_is_null(v), sql_is_not_null(sort.expr)])
                and_predicates.append(sql_any([comp, null]))
            or_predicates.append(sql_all(and_predicates))
        return sql_any(or_predicates)

    async def fetch_raw_query(self, query: "SessionRawQuery") -> list[Row]:
        return await self._backend.fetch_raw(query.fragment, query.params)

    _mappings: dict[type, EntityMapping]

    def get_mapping(self, entity_type: type):
        return self._mappings[entity_type]


class SQLBuildingContext:
    def __init__(self, start_pointer: int = 0):
        self._param_pointer = start_pointer

    _patt_word = re.compile(r"('[^']*'|\"[^\"]*\"|\s+|::|:\w+|\w+|[^\w\s])")
    _patt_param = re.compile(r":(\w+)")

    def parse(self, sql: str, params: dict[str, Value]):
        tokens = list[SQL]()
        words: list[str] = self._patt_word.findall(sql)
        param_index_map = dict[str, int]()
        param_map = ParamMap()

        for word in words:
            if matched := self._patt_param.match(word):
                param_name = matched[1]
                assert param_name in params, f"Parameter '{param_name}' not provided"
                param_id = param_index_map.get(param_name)
                if param_id is None:
                    param_id = self.new_param_id()
                    param_index_map[param_name] = param_id
                    param_map[param_id] = params[param_name]
                tokens.append(sql_param(param_id))
            else:
                tokens.append(sql_text(word))

        return sql_fragment(tokens), param_map

    def new_param_id(self):
        param_id = self._param_pointer
        self._param_pointer += 1
        return param_id


class SQLRenderingContext:
    def __init__(self):
        self._param_locs = dict[typing.Hashable, int]()

    def locate_param(self, id: typing.Hashable):
        return self._param_locs.setdefault(id, len(self._param_locs))

    def get_param_keys(self):
        return list(self._param_locs.keys())


class SessionEntityQuery(typing.Generic[TEntity]):
    def __init__(self, session: Session, mapping: EntityMapping, alias: str):
        self._session = session
        self.mapping = mapping
        self.alias = alias
        self.params = ParamMap()
        self.joins = dict[str, SQLQuery.Join]()
        self.where_conds = list[SQL]()
        self.having_conds = list[SQL]()
        self.order_by_opts = tuple[SQLQuery.OrderBy, ...]()
        self.group_by_exprs = list[SQL]()
        self.ctx = SQLBuildingContext()

    def join(self, target: type | str, alias: str, on: str, **params: Value) -> Self:
        self.joins[alias] = SQLQuery.Join(
            type="JOIN",
            table=self._get_target(target, params),
            alias=sql_n(alias),
            on=self._parse(on, params),
        )
        return self

    def left_join(self, target: type | str, alias: str, on: str, **params: Value) -> Self:
        self.joins[alias] = SQLQuery.Join(
            type="LEFT JOIN",
            table=self._get_target(target, params),
            alias=sql_n(alias),
            on=self._parse(on, params),
        )
        return self

    def where(self, condition: str, **params: Value) -> Self:
        self.where_conds.append(self._parse(f"({condition})", params))
        return self

    def having(self, condition: str, **params: Value) -> Self:
        self.having_conds.append(self._parse(f"({condition})", params))
        return self

    def group_by_primary_key(self) -> Self:
        self.group_by_exprs.extend(sql_qn(self.alias, f.column) for f in self.mapping.get_primary_fields())
        return self

    def order_by(self, *order_by: SQLQuery.OrderBy) -> Self:
        self.order_by_opts = order_by
        return self

    async def fetch(self, limit: int | None = None, offset: int | None = None) -> list[TEntity]:
        return await self._session.fetch_session_entity_query(self, limit, offset)
        # return typing.cast(list[TEntity], entities)

    async def fetch_one(self) -> TEntity | None:
        results = await self.fetch(limit=1, offset=0)
        return results[0] if results else None

    async def count(self) -> int:
        return await self._session.count_session_entity_query(self)

    async def paginate(
        self,
        first: int | None = None,
        after: KeyLike | None = None,
        last: int | None = None,
        before: KeyLike | None = None,
        offset: int | None = None,
    ) -> Session.Page:
        opts = Session.PageOpts(first, after, last, before, offset)
        return await self._session.paginate_session_entity_query(self, opts)

    def asc(self, expr: str, nulls_last: bool = True, **params: Value) -> SQLQuery.OrderBy:
        return SQLQuery.OrderBy(self._parse(expr, params), True, nulls_last)

    def desc(self, expr: str, nulls_last: bool = True, **params: Value) -> SQLQuery.OrderBy:
        return SQLQuery.OrderBy(self._parse(expr, params), False, nulls_last)

    def _get_target(self, target: type | str, params: dict[str, Value]):
        if isinstance(target, str):
            return self._parse(target, params)
        target_mapping = self._session.get_mapping(target)
        return sql_qn(target_mapping.schema, target_mapping.table)

    def _parse(self, sql: str, params: dict[str, Value]):
        fragment, param_map = self.ctx.parse(sql, params)
        self.params.update(param_map)
        return fragment


class SessionRawQuery:
    def __init__(self, session: "Session", query: str, params: dict[str, Value]):
        self._session = session
        self.fragment, self.params = SQLBuildingContext().parse(query, params)

    async def fetch(self):
        return await self._session.fetch_raw_query(self)

    async def fetch_one(self):
        results = await self.fetch()
        return results[0] if results else None


class AsyncPGSessionBackend(SessionBackend):
    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool
        self._active: asyncpg.Pool | asyncpg.Connection = pool
        self._tx: asyncpg.transaction.Transaction | None = None

    async def select(self, stmt: SQLSelect, values: list[ParamMap]) -> list[Row]:
        query, param_lists = self.Renderer().render_select(stmt, values)
        return await self._active.fetchmany(query, param_lists)

    async def insert(self, stmt: SQLInsert, values: list[ParamMap]) -> list[Row]:
        query, param_lists = self.Renderer().render_insert(stmt, values)
        return await self._active.fetchmany(query, param_lists)

    async def update(self, stmt: SQLUpdate, values: list[ParamMap]) -> list[Row]:
        query, param_lists = self.Renderer().render_update(stmt, values)
        return await self._active.fetchmany(query, param_lists)

    async def delete(self, stmt: SQLDelete, values: list[ParamMap]) -> None:
        query, param_lists = self.Renderer().render_delete(stmt, values)
        await self._active.fetchmany(query, param_lists)

    async def fetch_query(self, stmt: SQLQuery, param_map: ParamMap) -> list[Row]:
        query, param_list = self.Renderer().render_query(stmt, param_map)
        rows = await self._active.fetch(query, *param_list)
        return [tuple(row) for row in rows]

    async def count_query(self, stmt: SQLQuery, param_map: ParamMap) -> int:
        query, param_list = self.Renderer().render_count(stmt, param_map)
        rows = await self._active.fetch(query, *param_list)
        return rows[0][0]

    async def fetch_raw(self, raw: SQL, param_map: ParamMap) -> list[Row]:
        query, param_list = self.Renderer().render_raw(raw, param_map)
        return await self._active.fetch(query, *param_list)

    async def begin(self) -> None:
        assert not self._tx
        conn: asyncpg.Connection = await self._pool.acquire()
        tx: asyncpg.transaction.Transaction = conn.transaction()
        await tx.start()
        self._active = conn
        self._tx = tx

    async def commit(self) -> None:
        assert self._tx
        try:
            await self._tx.commit()
        finally:
            await self._pool.release(self._active)
            self._active = self._pool
            self._tx = None

    async def rollback(self) -> None:
        assert self._tx
        try:
            await self._tx.rollback()
        finally:
            await self._pool.release(self._active)
            self._active = self._pool
            self._tx = None

    async def savepoint(self, name: str) -> None:
        await self._active.execute(f"SAVEPOINT {name}")

    async def release(self, name: str) -> None:
        await self._active.execute(f"RELEASE SAVEPOINT {name}")

    async def rollback_to(self, name: str) -> None:
        await self._active.execute(f"ROLLBACK TO SAVEPOINT {name}")

    class Renderer:
        def __init__(self):
            self._ctx = SQLRenderingContext()

        def render_select(self, stmt: SQLSelect, param_maps: list[ParamMap]):
            parts = ["SELECT"]
            parts.append(", ".join(self._el(sql_n(c)) for c in stmt.select))
            parts.append(f"FROM {self._el(sql_qn(stmt.from_schema, stmt.from_table))}")
            parts.append(f"WHERE {' AND '.join([f'{self._el(sql_n(c))} = {self._el(sql_param(c))}' for c in stmt.key_columns])}")
            query = " ".join(parts)
            param_lists = [[param_map[id] for id in self._ctx.get_param_keys()] for param_map in param_maps]
            return query, param_lists

        def render_insert(self, stmt: SQLInsert, param_maps: list[ParamMap]):
            parts = ["INSERT INTO", self._el(sql_qn(stmt.into_schema, stmt.into_table))]
            parts.append(f"({', '.join(self._el(sql_n(c)) for c in stmt.insert)})")
            parts.append(f"VALUES ({', '.join(self._el(sql_param(c)) for c in stmt.insert)})")
            parts.append(f"RETURNING {', '.join(self._el(sql_n(c)) for c in stmt.returning)}")
            query = " ".join(parts)
            param_lists = [[param_map[id] for id in self._ctx.get_param_keys()] for param_map in param_maps]
            return query, param_lists

        def render_update(self, stmt: SQLUpdate, param_maps: list[ParamMap]):
            parts = ["UPDATE", self._el(sql_qn(stmt.schema, stmt.table))]
            parts.append(f"SET {', '.join(f'{self._el(sql_n(c))} = {self._el(sql_param(c))}' for c in stmt.sets)}")
            parts.append(f"WHERE {' AND '.join([f'{self._el(sql_n(c))} = {self._el(sql_param(c))}' for c in stmt.where])}")
            parts.append(f"RETURNING {', '.join(self._el(sql_n(c)) for c in stmt.returning)}")
            query = " ".join(parts)
            param_lists = [[param_map[id] for id in self._ctx.get_param_keys()] for param_map in param_maps]
            return query, param_lists

        def render_delete(self, stmt: SQLDelete, param_maps: list[ParamMap]):
            parts = ["DELETE FROM", self._el(sql_qn(stmt.from_schema, stmt.from_table))]
            parts.append(f"WHERE {' AND '.join([f'{self._el(sql_n(c))} = {self._el(sql_param(c))}' for c in stmt.key_columns])}")
            query = " ".join(parts)
            param_lists = [[param_map[id] for id in self._ctx.get_param_keys()] for param_map in param_maps]
            return query, param_lists

        def render_query(self, stmt: SQLQuery, param_map: ParamMap):
            parts = ["SELECT"]
            parts.append(", ".join(self._el(c) for c in stmt.select))
            parts.append(f"FROM {self._el(stmt.from_table)} AS {self._el(stmt.from_alias)}")
            for join in stmt.joins:
                parts.append(self._sql_join_opt(join))
            if stmt.where:
                parts.append(f"WHERE {self._el(stmt.where)}")
            if stmt.group_by:
                parts.append(f"GROUP BY {', '.join(self._el(c) for c in stmt.group_by)}")
            if stmt.having:
                parts.append(f"HAVING {self._el(stmt.having)}")
            if stmt.order_bys:
                parts.append(f"ORDER BY {', '.join(self._sql_order_opt(opt) for opt in stmt.order_bys)}")
            if stmt.limit:
                parts.append(f"LIMIT {self._el(stmt.limit)}")
            if stmt.offset:
                parts.append(f"OFFSET {self._el(stmt.offset)}")
            query = " ".join(parts)
            params = [param_map[id] for id in self._ctx.get_param_keys()]

            return query, params

        def render_count(self, stmt: SQLQuery, param_map: ParamMap):
            select_query, params = self.render_query(stmt, param_map)
            return f"SELECT COUNT(*) FROM ({select_query}) AS _", params

        def render_raw(self, raw: SQL, param_map: ParamMap):
            query = self._el(raw)
            params = [param_map[id] for id in self._ctx.get_param_keys()]
            return query, params

        def _sql_join_opt(self, opt: SQLQuery.Join):
            return f"{opt.type} {self._el(opt.table)} {self._el(opt.alias)} ON {self._el(opt.on)}"

        def _sql_order_opt(self, opt: SQLQuery.OrderBy):
            direction = "ASC" if opt.ascending else "DESC"
            nulls = "NULLS LAST" if opt.nulls_last else "NULLS FIRST"
            return f"{self._el(opt.expr)} {direction} {nulls}"

        def _el(self, el: SQL) -> str:
            match el:
                case sql_n(part1):
                    return f'"{part1.replace(".", '"."')}"'
                case sql_qn(part1, part2):
                    return f'"{part1.replace(".", '"."')}"."{part2.replace('"', '""')}"'
                case sql_text(text):
                    return text
                case sql_param(id):
                    return f"${self._ctx.locate_param(id) + 1}"
                case sql_all(els):
                    return f"({' AND '.join(self._el(e) for e in els)})"
                case sql_any(els):
                    return f"({' OR '.join(self._el(e) for e in els)})"
                case sql_eq(left, right):
                    return f"({self._el(left)} = {self._el(right)})"
                case sql_lt(left, right):
                    return f"({self._el(left)} < {self._el(right)})"
                case sql_gt(left, right):
                    return f"({self._el(left)} > {self._el(right)})"
                case sql_is_null(expr):
                    return f"({self._el(expr)} IS NULL)"
                case sql_is_not_null(expr):
                    return f"({self._el(expr)} IS NOT NULL)"
                case sql_fragment(elements):
                    return "".join(self._el(e) for e in elements)


class AutoMappingBuilder:
    class FieldConfig(typing.TypedDict, total=False):
        column: str
        skip_on_insert: bool
        skip_on_update: bool

    class ChildConfig(typing.TypedDict):
        kind: typing.Literal["singular", "plural"]
        target: type | typing.Callable[[], type]

    class EntityMappingConfig(typing.TypedDict, total=False):
        schema: str
        table: str
        primary_key: str | Collection[str]
        parental_key: str | Collection[str]
        fields: dict[str, "AutoMappingBuilder.FieldConfig"]
        children: dict[str, "AutoMappingBuilder.ChildConfig"]
        factory: EntityFactory

    def __init__(self):
        self._configs = dict[type, self.EntityMappingConfig]()
        self._mappings = dict[type, EntityMapping]()

    def map(self, entity_type: type[TEntity], **kwargs: typing.Unpack[EntityMappingConfig]) -> type[TEntity]:
        self._configs[entity_type] = kwargs
        return entity_type

    def mapped(self, **kwargs: typing.Unpack[EntityMappingConfig]) -> typing.Callable[[type[TEntity]], type[TEntity]]:
        return lambda entity_type: self.map(entity_type, **kwargs)

    def build(self):
        mappings = list[EntityMapping]()
        for cls, opts in self._configs.items():
            if cls in self._mappings:
                mappings.append(self._mappings[cls])
            else:
                mapping = self._build_entity_mapping(cls, opts)
                mappings.append(mapping)
                self._mappings[cls] = mapping

        return mappings

    def _build_entity_mapping(self, entity_type: type, opts: EntityMappingConfig):
        field_configs = dict(opts.get("fields", ()))
        child_configs = dict(opts.get("children", ()))

        for name, type_hint in typing.get_type_hints(entity_type).items():
            origin = typing.get_origin(type_hint)
            args = typing.get_args(type_hint)
            # skip private fields
            if name.startswith("_"):
                continue
            # skip registered fields
            elif name in field_configs or name in child_configs:
                continue
            # list of registered entity
            elif origin is list and args[0] in self._configs:
                child_configs[name] = self.ChildConfig(kind="plural", target=args[0])
            # registered entity
            elif type_hint in self._configs:
                child_configs[name] = self.ChildConfig(kind="singular", target=type_hint)
            # optional of registered entity
            elif origin in (types.UnionType, typing.Union) and len(args) == 2 and args[1] is type(None) and args[0] in self._configs:
                child_configs[name] = self.ChildConfig(kind="singular", target=args[0])
            else:
                field_configs[name] = self.FieldConfig(column=self._column_name(name))

        fields = {name: self._build_field(name, config) for name, config in field_configs.items()}
        children = {name: self._build_child(name, config) for name, config in child_configs.items()}

        primary = opts.get("primary_key", ["id"])
        primary = [primary] if isinstance(primary, str) else list(primary)
        parental = opts.get("parental_key", [])
        parental = [parental] if isinstance(parental, str) else list(parental)
        skip_on_insert = [fn for fn, fc in field_configs.items() if fc.get("skip_on_insert")]
        skip_on_update = [fn for fn, fc in field_configs.items() if fc.get("skip_on_update")]
        insertable = [fn for fn in fields if fn not in skip_on_insert]
        updatable = [fn for fn in fields if not (fn in skip_on_update or fn in primary or fn in parental)]

        return EntityMapping(
            entity_type=entity_type,
            schema=opts.get("schema", "public"),
            table=opts.get("table", self._table_name(entity_type.__name__)),
            fields=fields,
            children=children,
            entity_factory=opts.get("factory", DefaultEntityFactory(entity_type)),
            primary_key=primary,
            parental_key=parental,
            insertable=insertable,
            updatable=updatable,
        )

    def _build_field(self, name: str, config: FieldConfig):
        column = config["column"] if "column" in config else self._column_name(name)
        return Field(name, column, FieldAttributeAccessor(name))

    def _build_child(self, name: str, config: ChildConfig):
        target = config["target"] if isinstance(config["target"], type) else config["target"]()
        if config["kind"] == "singular":
            return Child(target, SingularChildAttributeAccessor(name))
        else:
            return Child(target, PluralChildAttributeAccessor(name))

    _name_patt = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")

    def _column_name(self, s: str):
        return self._name_patt.sub("_", s).lower()

    def _table_name(self, s: str):
        return self._name_patt.sub("_", s).lower()


class FieldAttributeAccessor(typing.NamedTuple):
    name: str

    def get(self, entity: Entity) -> Value:
        return getattr(entity, self.name, None)

    def set(self, entity: Entity, value: Value):
        setattr(entity, self.name, value)


class SingularChildAttributeAccessor(typing.NamedTuple):
    name: str

    def get(self, entity: Entity) -> Sequence[Entity]:
        return tuple(i for i in (getattr(entity, self.name), None) if i is not None)

    def set(self, entity: Entity, value: Sequence[Entity]):
        setattr(entity, self.name, next(iter(value), None))


class PluralChildAttributeAccessor(typing.NamedTuple):
    name: str

    def get(self, entity: Entity) -> Sequence[Entity]:
        return getattr(entity, self.name, ())

    def set(self, entity: Entity, value: Sequence[Entity]):
        setattr(entity, self.name, list(value))


class DefaultEntityFactory(typing.NamedTuple):
    entity_type: type

    def create(self) -> Entity:
        return typing.cast(Entity, object.__new__(self.entity_type))


auto = AutoMappingBuilder()
