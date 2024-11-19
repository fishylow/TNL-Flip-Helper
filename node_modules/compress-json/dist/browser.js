"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const core_1 = require("./core");
const helpers_1 = require("./helpers");
const memory_1 = require("./memory");
const compressJSON = {
    compress: core_1.compress,
    decompress: core_1.decompress,
    decode: core_1.decode,
    addValue: memory_1.addValue,
    trimUndefined: helpers_1.trimUndefined,
    trimUndefinedRecursively: helpers_1.trimUndefinedRecursively,
};
Object.assign(window, { compressJSON });
