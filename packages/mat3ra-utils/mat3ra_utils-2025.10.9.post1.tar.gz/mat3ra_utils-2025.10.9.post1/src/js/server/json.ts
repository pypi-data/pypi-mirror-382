import fs from "fs";
import path from "path";

import { createDirIfNotExistsSync } from "./file";

type Replacer = Parameters<typeof JSON.stringify>[1];
type Space = Parameters<typeof JSON.stringify>[2];

type WriteJSONOptions = {
    replacer?: Replacer;
    spaces?: Space;
    addNewLine?: boolean;
};

export function readJSONFileSync(filePath: string): object {
    const content = fs.readFileSync(filePath, "utf-8");
    return JSON.parse(content);
}

export function writeJSONFileSync(
    filePath: string,
    data: unknown,
    { replacer, spaces = 0, addNewLine = true }: WriteJSONOptions = {},
) {
    createDirIfNotExistsSync(path.dirname(filePath));
    const json = JSON.stringify(data, replacer, spaces) + (addNewLine ? "\n" : "");
    fs.writeFileSync(filePath, json, "utf-8");
}
