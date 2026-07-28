import { readFileSync } from "node:fs";
import { join } from "node:path";
import { Index, Problem } from "./schema";

const DIR = join(process.cwd(), "traces");

const read = (file: string) => JSON.parse(readFileSync(join(DIR, file), "utf8"));

/** Parsing here means `next build` is the schema verification step. */
export const getIndex = () => Index.parse(read("index.json"));
export const getProblem = (slug: string) => Problem.parse(read(`${slug}.json`));
