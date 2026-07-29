/**
 * Derive the API-facing JSON Schema from lib/schema.ts. Nothing here is hand
 * written: two schemas maintained side by side drift, and a drifted schema is
 * a generator that produces traces the player cannot parse.
 *
 *   node pipeline/schema-json.mts          # rewrite prompts/solve-schema.json
 *   node pipeline/schema-json.mts --check  # fail if the committed file is stale
 *
 * `.mts` because tsconfig includes `**\/*.ts` and this is not app code; node's
 * type stripping runs it directly, so there is no build step and no dep.
 *
 * OpenAI strict mode cannot express three things schemaVersion 1 uses, so the
 * transform rewrites them mechanically and api/_gen.py reverses each one:
 *
 *   optional key   ->  required key, nullable union, marked "x-optional"
 *   tuple          ->  object {_0, _1, ...}          (no prefixItems in strict)
 *   record<K,V>    ->  object {"$entries": [{key, value}]}  (no open maps)
 *
 * The `$entries` wrapper matters: encoding a record as a bare pair array would
 * be indistinguishable from a genuine array of two-key objects inside `Val`.
 */

import { readFileSync, writeFileSync } from "node:fs";
import { Problem } from "../lib/schema.ts";

type JS = Record<string, any>;

const OUT = new URL("../prompts/solve-schema.json", import.meta.url);
const defs: JS = {};
const lazies = new Map<unknown, string>();

const object = (properties: JS): JS => ({
  type: "object",
  properties,
  required: Object.keys(properties),
  additionalProperties: false,
});

/** Strict mode has no optional keys, so absence is modelled as an explicit null. */
function nullable(s: JS): JS {
  if (Array.isArray(s.anyOf)) {
    if (!s.anyOf.some((o: JS) => o.type === "null")) s.anyOf.push({ type: "null" });
    return s;
  }
  if (Array.isArray(s.type)) return s; // already a nullable union (z.nullish())
  // A plain scalar becomes a type union; anything with an enum or a $ref keeps
  // its own shape and gets null as a sibling branch instead.
  if (typeof s.type === "string" && !s.enum) return { ...s, type: [s.type, "null"] };
  return { anyOf: [s, { type: "null" }] };
}

/** Unwraps the wrappers that mean "the key may be absent". */
function peel(t: any): [any, boolean] {
  const n = t._def.typeName;
  if (n === "ZodOptional" || n === "ZodDefault") return [peel(t._def.innerType)[0], true];
  return [t, false];
}

function conv(t: any): JS {
  const d = t._def;
  switch (d.typeName) {
    case "ZodLazy": {
      let name = lazies.get(t);
      if (!name) {
        name = `Rec${lazies.size}`;
        lazies.set(t, name);
        defs[name] = {}; // registered before recursing, or the recursion never ends
        Object.assign(defs[name], conv(d.getter()));
      }
      return { $ref: `#/$defs/${name}` };
    }
    case "ZodString":
      return { type: "string" };
    case "ZodNumber":
      return { type: "number" };
    case "ZodBoolean":
      return { type: "boolean" };
    case "ZodNull":
      return { type: "null" };
    case "ZodLiteral":
      return { type: typeof d.value === "number" ? "number" : typeof d.value, enum: [d.value] };
    case "ZodEnum":
      return { type: "string", enum: [...d.values] };
    case "ZodArray":
      // min()/max() are dropped: strict mode ignores them. api/_gen.py's
      // semantic validation re-asserts every .min(1) instead.
      return { type: "array", items: conv(d.type) };
    case "ZodUnion":
      return { anyOf: d.options.map(conv) };
    case "ZodNullable":
      return nullable(conv(d.innerType));
    case "ZodTuple":
      return object(Object.fromEntries(d.items.map((it: any, i: number) => [`_${i}`, conv(it)])));
    case "ZodRecord":
      return object({
        $entries: {
          type: "array",
          items: object({ key: conv(d.keyType), value: conv(d.valueType) }),
        },
      });
    case "ZodObject": {
      const props: JS = {};
      for (const [k, v] of Object.entries<any>(d.shape())) {
        const [inner, optional] = peel(v);
        props[k] = optional ? nullable(conv(inner)) : conv(inner);
        if (optional) props[k]["x-optional"] = true;
      }
      return object(props);
    }
  }
  throw new Error(`unhandled zod node: ${d.typeName} — teach the transform, do not hand-write JSON`);
}

const built =
  JSON.stringify(
    { name: "leetviz_trace", strict: true, schema: { ...conv(Problem), $defs: defs } },
    null,
    2
  ) + "\n";

if (process.argv.includes("--check")) {
  let have = "";
  try {
    have = readFileSync(OUT, "utf8");
  } catch {
    /* missing counts as stale */
  }
  if (have !== built) {
    console.error(
      "STALE: prompts/solve-schema.json does not match lib/schema.ts.\n" +
        "Run `pnpm schema` and commit the result."
    );
    process.exit(1);
  }
  console.log("prompts/solve-schema.json is in sync with lib/schema.ts");
} else {
  writeFileSync(OUT, built);
  console.log(`wrote prompts/solve-schema.json (${built.length} bytes)`);
}
