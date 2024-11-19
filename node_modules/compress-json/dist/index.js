"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.config = exports.trimUndefinedRecursively = exports.trimUndefined = exports.addValue = exports.decode = exports.decompress = exports.compress = void 0;
/* for direct usage */
var core_1 = require("./core");
Object.defineProperty(exports, "compress", { enumerable: true, get: function () { return core_1.compress; } });
Object.defineProperty(exports, "decompress", { enumerable: true, get: function () { return core_1.decompress; } });
/* for custom wrapper */
var core_2 = require("./core");
Object.defineProperty(exports, "decode", { enumerable: true, get: function () { return core_2.decode; } });
var memory_1 = require("./memory");
Object.defineProperty(exports, "addValue", { enumerable: true, get: function () { return memory_1.addValue; } });
/* to remove undefined object fields */
var helpers_1 = require("./helpers");
Object.defineProperty(exports, "trimUndefined", { enumerable: true, get: function () { return helpers_1.trimUndefined; } });
Object.defineProperty(exports, "trimUndefinedRecursively", { enumerable: true, get: function () { return helpers_1.trimUndefinedRecursively; } });
/* to config */
var config_1 = require("./config");
Object.defineProperty(exports, "config", { enumerable: true, get: function () { return config_1.config; } });
