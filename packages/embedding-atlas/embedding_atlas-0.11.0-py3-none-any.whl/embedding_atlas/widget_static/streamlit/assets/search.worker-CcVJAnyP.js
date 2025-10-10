var y;
function R(t, i, e) {
  const s = typeof e, n = typeof t;
  if (s !== "undefined") {
    if (n !== "undefined") {
      if (e) {
        if (n === "function" && s === n) return function(o) {
          return t(e(o));
        };
        if (i = t.constructor, i === e.constructor) {
          if (i === Array) return e.concat(t);
          if (i === Map) {
            var r = new Map(e);
            for (var h of t) r.set(h[0], h[1]);
            return r;
          }
          if (i === Set) {
            h = new Set(e);
            for (r of t.values()) h.add(r);
            return h;
          }
        }
      }
      return t;
    }
    return e;
  }
  return n === "undefined" ? i : t;
}
function U(t, i) {
  return typeof t > "u" ? i : t;
}
function I() {
  return /* @__PURE__ */ Object.create(null);
}
function N(t) {
  return typeof t == "string";
}
function lt(t) {
  return typeof t == "object";
}
function ot(t, i) {
  if (N(i)) t = t[i];
  else for (let e = 0; t && e < i.length; e++) t = t[i[e]];
  return t;
}
const fe = /[^\p{L}\p{N}]+/u, ue = /(\d{3})/g, ce = /(\D)(\d{3})/g, ge = /(\d{3})(\D)/g, Wt = /[\u0300-\u036f]/g;
function ft(t = {}) {
  if (!this || this.constructor !== ft) return new ft(...arguments);
  if (arguments.length) for (t = 0; t < arguments.length; t++) this.assign(arguments[t]);
  else this.assign(t);
}
y = ft.prototype;
y.assign = function(t) {
  this.normalize = R(t.normalize, !0, this.normalize);
  let i = t.include, e = i || t.exclude || t.split, s;
  if (e || e === "") {
    if (typeof e == "object" && e.constructor !== RegExp) {
      let n = "";
      s = !i, i || (n += "\\p{Z}"), e.letter && (n += "\\p{L}"), e.number && (n += "\\p{N}", s = !!i), e.symbol && (n += "\\p{S}"), e.punctuation && (n += "\\p{P}"), e.control && (n += "\\p{C}"), (e = e.char) && (n += typeof e == "object" ? e.join("") : e);
      try {
        this.split = new RegExp("[" + (i ? "^" : "") + n + "]+", "u");
      } catch {
        this.split = /\s+/;
      }
    } else this.split = e, s = e === !1 || "a1a".split(e).length < 2;
    this.numeric = R(t.numeric, s);
  } else {
    try {
      this.split = R(this.split, fe);
    } catch {
      this.split = /\s+/;
    }
    this.numeric = R(t.numeric, R(this.numeric, !0));
  }
  if (this.prepare = R(t.prepare, null, this.prepare), this.finalize = R(t.finalize, null, this.finalize), e = t.filter, this.filter = typeof e == "function" ? e : R(e && new Set(e), null, this.filter), this.dedupe = R(t.dedupe, !0, this.dedupe), this.matcher = R((e = t.matcher) && new Map(e), null, this.matcher), this.mapper = R((e = t.mapper) && new Map(e), null, this.mapper), this.stemmer = R(
    (e = t.stemmer) && new Map(e),
    null,
    this.stemmer
  ), this.replacer = R(t.replacer, null, this.replacer), this.minlength = R(t.minlength, 1, this.minlength), this.maxlength = R(t.maxlength, 1024, this.maxlength), this.rtl = R(t.rtl, !1, this.rtl), (this.cache = e = R(t.cache, !0, this.cache)) && (this.F = null, this.L = typeof e == "number" ? e : 2e5, this.B = /* @__PURE__ */ new Map(), this.D = /* @__PURE__ */ new Map(), this.I = this.H = 128), this.h = "", this.J = null, this.A = "", this.K = null, this.matcher) for (const n of this.matcher.keys()) this.h += (this.h ? "|" : "") + n;
  if (this.stemmer) for (const n of this.stemmer.keys()) this.A += (this.A ? "|" : "") + n;
  return this;
};
y.addStemmer = function(t, i) {
  return this.stemmer || (this.stemmer = /* @__PURE__ */ new Map()), this.stemmer.set(t, i), this.A += (this.A ? "|" : "") + t, this.K = null, this.cache && D(this), this;
};
y.addFilter = function(t) {
  return typeof t == "function" ? this.filter = t : (this.filter || (this.filter = /* @__PURE__ */ new Set()), this.filter.add(t)), this.cache && D(this), this;
};
y.addMapper = function(t, i) {
  return typeof t == "object" ? this.addReplacer(t, i) : t.length > 1 ? this.addMatcher(t, i) : (this.mapper || (this.mapper = /* @__PURE__ */ new Map()), this.mapper.set(t, i), this.cache && D(this), this);
};
y.addMatcher = function(t, i) {
  return typeof t == "object" ? this.addReplacer(t, i) : t.length < 2 && (this.dedupe || this.mapper) ? this.addMapper(t, i) : (this.matcher || (this.matcher = /* @__PURE__ */ new Map()), this.matcher.set(t, i), this.h += (this.h ? "|" : "") + t, this.J = null, this.cache && D(this), this);
};
y.addReplacer = function(t, i) {
  return typeof t == "string" ? this.addMatcher(t, i) : (this.replacer || (this.replacer = []), this.replacer.push(t, i), this.cache && D(this), this);
};
y.encode = function(t, i) {
  if (this.cache && t.length <= this.H) if (this.F) {
    if (this.B.has(t)) return this.B.get(t);
  } else this.F = setTimeout(D, 50, this);
  this.normalize && (typeof this.normalize == "function" ? t = this.normalize(t) : t = Wt ? t.normalize("NFKD").replace(Wt, "").toLowerCase() : t.toLowerCase()), this.prepare && (t = this.prepare(t)), this.numeric && t.length > 3 && (t = t.replace(ce, "$1 $2").replace(ge, "$1 $2").replace(ue, "$1 "));
  const e = !(this.dedupe || this.mapper || this.filter || this.matcher || this.stemmer || this.replacer);
  let s = [], n = I(), r, h, o = this.split || this.split === "" ? t.split(this.split) : [t];
  for (let f = 0, u, g; f < o.length; f++) if ((u = g = o[f]) && !(u.length < this.minlength || u.length > this.maxlength)) {
    if (i) {
      if (n[u]) continue;
      n[u] = 1;
    } else {
      if (r === u) continue;
      r = u;
    }
    if (e) s.push(u);
    else if (!this.filter || (typeof this.filter == "function" ? this.filter(u) : !this.filter.has(u))) {
      if (this.cache && u.length <= this.I) if (this.F) {
        var l = this.D.get(u);
        if (l || l === "") {
          l && s.push(l);
          continue;
        }
      } else this.F = setTimeout(D, 50, this);
      if (this.stemmer) {
        this.K || (this.K = new RegExp("(?!^)(" + this.A + ")$"));
        let m;
        for (; m !== u && u.length > 2; ) m = u, u = u.replace(this.K, (d) => this.stemmer.get(d));
      }
      if (u && (this.mapper || this.dedupe && u.length > 1)) {
        l = "";
        for (let m = 0, d = "", a, c; m < u.length; m++) a = u.charAt(m), a === d && this.dedupe || ((c = this.mapper && this.mapper.get(a)) || c === "" ? c === d && this.dedupe || !(d = c) || (l += c) : l += d = a);
        u = l;
      }
      if (this.matcher && u.length > 1 && (this.J || (this.J = new RegExp("(" + this.h + ")", "g")), u = u.replace(this.J, (m) => this.matcher.get(m))), u && this.replacer) for (l = 0; u && l < this.replacer.length; l += 2) u = u.replace(
        this.replacer[l],
        this.replacer[l + 1]
      );
      if (this.cache && g.length <= this.I && (this.D.set(g, u), this.D.size > this.L && (this.D.clear(), this.I = this.I / 1.1 | 0)), u) {
        if (u !== g) if (i) {
          if (n[u]) continue;
          n[u] = 1;
        } else {
          if (h === u) continue;
          h = u;
        }
        s.push(u);
      }
    }
  }
  return this.finalize && (s = this.finalize(s) || s), this.cache && t.length <= this.H && (this.B.set(t, s), this.B.size > this.L && (this.B.clear(), this.H = this.H / 1.1 | 0)), s;
};
function D(t) {
  t.F = null, t.B.clear(), t.D.clear();
}
function Pt(t, i, e) {
  e || (i || typeof t != "object" ? typeof i == "object" && (e = i, i = 0) : e = t), e && (t = e.query || t, i = e.limit || i);
  let s = "" + (i || 0);
  e && (s += (e.offset || 0) + !!e.context + !!e.suggest + (e.resolve !== !1) + (e.resolution || this.resolution) + (e.boost || 0)), t = ("" + t).toLowerCase(), this.cache || (this.cache = new G());
  let n = this.cache.get(t + s);
  if (!n) {
    const r = e && e.cache;
    r && (e.cache = !1), n = this.search(t, i, e), r && (e.cache = r), this.cache.set(t + s, n);
  }
  return n;
}
function G(t) {
  this.limit = t && t !== !0 ? t : 1e3, this.cache = /* @__PURE__ */ new Map(), this.h = "";
}
G.prototype.set = function(t, i) {
  this.cache.set(this.h = t, i), this.cache.size > this.limit && this.cache.delete(this.cache.keys().next().value);
};
G.prototype.get = function(t) {
  const i = this.cache.get(t);
  return i && this.h !== t && (this.cache.delete(t), this.cache.set(this.h = t, i)), i;
};
G.prototype.remove = function(t) {
  for (const i of this.cache) {
    const e = i[0];
    i[1].includes(t) && this.cache.delete(e);
  }
};
G.prototype.clear = function() {
  this.cache.clear(), this.h = "";
};
const Jt = { normalize: !1, numeric: !1, dedupe: !1 }, pt = {}, St = /* @__PURE__ */ new Map([["b", "p"], ["v", "f"], ["w", "f"], ["z", "s"], ["x", "s"], ["d", "t"], ["n", "m"], ["c", "k"], ["g", "k"], ["j", "k"], ["q", "k"], ["i", "e"], ["y", "e"], ["u", "o"]]), Zt = /* @__PURE__ */ new Map([["ae", "a"], ["oe", "o"], ["sh", "s"], ["kh", "k"], ["th", "t"], ["ph", "f"], ["pf", "f"]]), Qt = [/([^aeo])h(.)/g, "$1$2", /([aeo])h([^aeo]|$)/g, "$1$2", /(.)\1+/g, "$1"], Vt = { a: "", e: "", i: "", o: "", u: "", y: "", b: 1, f: 1, p: 1, v: 1, c: 2, g: 2, j: 2, k: 2, q: 2, s: 2, x: 2, z: 2, ß: 2, d: 3, t: 3, l: 4, m: 5, n: 5, r: 6 };
var Et = { Exact: Jt, Default: pt, Normalize: pt, LatinBalance: { mapper: St }, LatinAdvanced: { mapper: St, matcher: Zt, replacer: Qt }, LatinExtra: { mapper: St, replacer: Qt.concat([/(?!^)[aeo]/g, ""]), matcher: Zt }, LatinSoundex: { dedupe: !1, include: { letter: !0 }, finalize: function(t) {
  for (let e = 0; e < t.length; e++) {
    var i = t[e];
    let s = i.charAt(0), n = Vt[s];
    for (let r = 1, h; r < i.length && (h = i.charAt(r), h === "h" || h === "w" || !(h = Vt[h]) || h === n || (s += h, n = h, s.length !== 4)); r++) ;
    t[e] = s;
  }
} }, CJK: { split: "" }, LatinExact: Jt, LatinDefault: pt, LatinSimple: pt };
function Xt(t, i, e, s) {
  let n = [];
  for (let r = 0, h; r < t.index.length; r++) if (h = t.index[r], i >= h.length) i -= h.length;
  else {
    i = h[s ? "splice" : "slice"](i, e);
    const o = i.length;
    if (o && (n = n.length ? n.concat(i) : i, e -= o, s && (t.length -= o), !e)) break;
    i = 0;
  }
  return n;
}
function et(t) {
  if (!this || this.constructor !== et) return new et(t);
  this.index = t ? [t] : [], this.length = t ? t.length : 0;
  const i = this;
  return new Proxy([], { get(e, s) {
    if (s === "length") return i.length;
    if (s === "push") return function(n) {
      i.index[i.index.length - 1].push(n), i.length++;
    };
    if (s === "pop") return function() {
      if (i.length) return i.length--, i.index[i.index.length - 1].pop();
    };
    if (s === "indexOf") return function(n) {
      let r = 0;
      for (let h = 0, o, l; h < i.index.length; h++) {
        if (o = i.index[h], l = o.indexOf(n), l >= 0) return r + l;
        r += o.length;
      }
      return -1;
    };
    if (s === "includes") return function(n) {
      for (let r = 0; r < i.index.length; r++) if (i.index[r].includes(n)) return !0;
      return !1;
    };
    if (s === "slice") return function(n, r) {
      return Xt(i, n || 0, r || i.length, !1);
    };
    if (s === "splice") return function(n, r) {
      return Xt(i, n || 0, r || i.length, !0);
    };
    if (s === "constructor") return Array;
    if (typeof s != "symbol") return (e = i.index[s / 2 ** 31 | 0]) && e[s];
  }, set(e, s, n) {
    return e = s / 2 ** 31 | 0, (i.index[e] || (i.index[e] = []))[s] = n, i.length++, !0;
  } });
}
et.prototype.clear = function() {
  this.index.length = 0;
};
et.prototype.push = function() {
};
function H(t = 8) {
  if (!this || this.constructor !== H) return new H(t);
  this.index = I(), this.h = [], this.size = 0, t > 32 ? (this.B = te, this.A = BigInt(t)) : (this.B = qt, this.A = t);
}
H.prototype.get = function(t) {
  const i = this.index[this.B(t)];
  return i && i.get(t);
};
H.prototype.set = function(t, i) {
  var e = this.B(t);
  let s = this.index[e];
  s ? (e = s.size, s.set(t, i), (e -= s.size) && this.size++) : (this.index[e] = s = /* @__PURE__ */ new Map([[t, i]]), this.h.push(s), this.size++);
};
function W(t = 8) {
  if (!this || this.constructor !== W) return new W(t);
  this.index = I(), this.h = [], this.size = 0, t > 32 ? (this.B = te, this.A = BigInt(t)) : (this.B = qt, this.A = t);
}
W.prototype.add = function(t) {
  var i = this.B(t);
  let e = this.index[i];
  e ? (i = e.size, e.add(t), (i -= e.size) && this.size++) : (this.index[i] = e = /* @__PURE__ */ new Set([t]), this.h.push(e), this.size++);
};
y = H.prototype;
y.has = W.prototype.has = function(t) {
  const i = this.index[this.B(t)];
  return i && i.has(t);
};
y.delete = W.prototype.delete = function(t) {
  const i = this.index[this.B(t)];
  i && i.delete(t) && this.size--;
};
y.clear = W.prototype.clear = function() {
  this.index = I(), this.h = [], this.size = 0;
};
y.values = W.prototype.values = function* () {
  for (let t = 0; t < this.h.length; t++) for (let i of this.h[t].values()) yield i;
};
y.keys = W.prototype.keys = function* () {
  for (let t = 0; t < this.h.length; t++) for (let i of this.h[t].keys()) yield i;
};
y.entries = W.prototype.entries = function* () {
  for (let t = 0; t < this.h.length; t++) for (let i of this.h[t].entries()) yield i;
};
function qt(t) {
  let i = 2 ** this.A - 1;
  if (typeof t == "number") return t & i;
  let e = 0, s = this.A + 1;
  for (let n = 0; n < t.length; n++) e = (e * s ^ t.charCodeAt(n)) & i;
  return this.A === 32 ? e + 2 ** 31 : e;
}
function te(t) {
  let i = BigInt(2) ** this.A - BigInt(1);
  var e = typeof t;
  if (e === "bigint") return t & i;
  if (e === "number") return BigInt(t) & i;
  e = BigInt(0);
  let s = this.A + BigInt(1);
  for (let n = 0; n < t.length; n++) e = (e * s ^ BigInt(t.charCodeAt(n))) & i;
  return e;
}
let E, ht;
async function pe(t) {
  t = t.data;
  var i = t.task;
  const e = t.id;
  let s = t.args;
  switch (i) {
    case "init":
      ht = t.options || {}, (i = t.factory) ? (Function("return " + i)()(self), E = new self.FlexSearch.Index(ht), delete self.FlexSearch) : E = new J(ht), postMessage({ id: e });
      break;
    default:
      let n;
      i === "export" && (s[1] ? (s[0] = ht.export, s[2] = 0, s[3] = 1) : s = null), i === "import" ? s[0] && (t = await ht.import.call(E, s[0]), E.import(s[0], t)) : ((n = s && E[i].apply(E, s)) && n.then && (n = await n), n && n.await && (n = await n.await), i === "search" && n.result && (n = n.result)), postMessage(i === "search" ? { id: e, msg: n } : { id: e });
  }
}
function $t(t) {
  q.call(t, "add"), q.call(t, "append"), q.call(t, "search"), q.call(t, "update"), q.call(t, "remove"), q.call(t, "searchCache");
}
let Bt, Yt, mt;
function de() {
  Bt = mt = 0;
}
function q(t) {
  this[t + "Async"] = function() {
    const i = arguments;
    var e = i[i.length - 1];
    let s;
    if (typeof e == "function" && (s = e, delete i[i.length - 1]), Bt ? mt || (mt = Date.now() - Yt >= this.priority * this.priority * 3) : (Bt = setTimeout(de, 0), Yt = Date.now()), mt) {
      const r = this;
      return new Promise((h) => {
        setTimeout(function() {
          h(r[t + "Async"].apply(r, i));
        }, 0);
      });
    }
    const n = this[t].apply(this, i);
    return e = n.then ? n : new Promise((r) => r(n)), s && e.then(s), e;
  };
}
let V = 0;
function it(t = {}, i) {
  function e(o) {
    function l(f) {
      f = f.data || f;
      const u = f.id, g = u && r.h[u];
      g && (g(f.msg), delete r.h[u]);
    }
    if (this.worker = o, this.h = I(), this.worker)
      return n ? this.worker.on("message", l) : this.worker.onmessage = l, t.config ? new Promise(function(f) {
        V > 1e9 && (V = 0), r.h[++V] = function() {
          f(r);
        }, r.worker.postMessage({ id: V, task: "init", factory: s, options: t });
      }) : (this.priority = t.priority || 4, this.encoder = i || null, this.worker.postMessage({ task: "init", factory: s, options: t }), this);
  }
  if (!this || this.constructor !== it) return new it(t);
  let s = typeof self < "u" ? self._factory : typeof window < "u" ? window._factory : null;
  s && (s = s.toString());
  const n = typeof window > "u", r = this, h = ae(s, n, t.worker);
  return h.then ? h.then(function(o) {
    return e.call(r, o);
  }) : e.call(this, h);
}
X("add");
X("append");
X("search");
X("update");
X("remove");
X("clear");
X("export");
X("import");
it.prototype.searchCache = Pt;
$t(it.prototype);
function X(t) {
  it.prototype[t] = function() {
    const i = this, e = [].slice.call(arguments);
    var s = e[e.length - 1];
    let n;
    return typeof s == "function" && (n = s, e.pop()), s = new Promise(function(r) {
      t === "export" && typeof e[0] == "function" && (e[0] = null), V > 1e9 && (V = 0), i.h[++V] = r, i.worker.postMessage({ task: t, id: V, args: e });
    }), n ? (s.then(n), this) : s;
  };
}
function ae(t, i, e) {
  return i ? typeof module < "u" ? new (require("worker_threads")).Worker(__dirname + "/worker/node.js") : Promise.resolve().then(function() {
    return _e;
  }).then(function(s) {
    return new s.Worker(import.meta.dirname + "/node/node.mjs");
  }) : t ? new window.Worker(URL.createObjectURL(new Blob(["onmessage=" + pe.toString()], { type: "text/javascript" }))) : new window.Worker(typeof e == "string" ? e : import.meta.url.replace("/worker.js", "/worker/worker.js").replace(
    "flexsearch.bundle.module.min.js",
    "module/worker/worker.js"
  ).replace("flexsearch.bundle.module.min.mjs", "module/worker/worker.js"), { type: "module" });
}
nt.prototype.add = function(t, i, e) {
  if (lt(t) && (i = t, t = ot(i, this.key)), i && (t || t === 0)) {
    if (!e && this.reg.has(t)) return this.update(t, i);
    for (let o = 0, l; o < this.field.length; o++) {
      l = this.B[o];
      var s = this.index.get(this.field[o]);
      if (typeof l == "function") {
        var n = l(i);
        n && s.add(t, n, e, !0);
      } else n = l.G, (!n || n(i)) && (l.constructor === String ? l = ["" + l] : N(l) && (l = [l]), Ct(i, l, this.D, 0, s, t, l[0], e));
    }
    if (this.tag) for (s = 0; s < this.A.length; s++) {
      var r = this.A[s];
      n = this.tag.get(this.F[s]);
      let o = I();
      if (typeof r == "function") {
        if (r = r(i), !r) continue;
      } else {
        var h = r.G;
        if (h && !h(i)) continue;
        r.constructor === String && (r = "" + r), r = ot(i, r);
      }
      if (n && r) {
        N(r) && (r = [r]);
        for (let l = 0, f, u; l < r.length; l++) if (f = r[l], !o[f] && (o[f] = 1, (h = n.get(f)) ? u = h : n.set(f, u = []), !e || !u.includes(t))) {
          if (u.length === 2 ** 31 - 1) {
            if (h = new et(u), this.fastupdate) for (let g of this.reg.values()) g.includes(u) && (g[g.indexOf(u)] = h);
            n.set(f, u = h);
          }
          u.push(t), this.fastupdate && ((h = this.reg.get(t)) ? h.push(u) : this.reg.set(t, [u]));
        }
      }
    }
    if (this.store && (!e || !this.store.has(t))) {
      let o;
      if (this.h) {
        o = I();
        for (let l = 0, f; l < this.h.length; l++) {
          if (f = this.h[l], (e = f.G) && !e(i)) continue;
          let u;
          if (typeof f == "function") {
            if (u = f(i), !u) continue;
            f = [f.O];
          } else if (N(f) || f.constructor === String) {
            o[f] = i[f];
            continue;
          }
          At(i, o, f, 0, f[0], u);
        }
      }
      this.store.set(t, o || i);
    }
    this.worker && (this.fastupdate || this.reg.add(t));
  }
  return this;
};
function At(t, i, e, s, n, r) {
  if (t = t[n], s === e.length - 1) i[n] = r || t;
  else if (t) if (t.constructor === Array) for (i = i[n] = Array(t.length), n = 0; n < t.length; n++) At(t, i, e, s, n);
  else i = i[n] || (i[n] = I()), n = e[++s], At(t, i, e, s, n);
}
function Ct(t, i, e, s, n, r, h, o) {
  if (t = t[h]) if (s === i.length - 1) {
    if (t.constructor === Array) {
      if (e[s]) {
        for (i = 0; i < t.length; i++) n.add(r, t[i], !0, !0);
        return;
      }
      t = t.join(" ");
    }
    n.add(r, t, o, !0);
  } else if (t.constructor === Array) for (h = 0; h < t.length; h++) Ct(t, i, e, s, n, r, h, o);
  else h = i[++s], Ct(t, i, e, s, n, r, h, o);
}
function Rt(t, i, e, s) {
  if (!t.length) return t;
  if (t.length === 1) return t = t[0], t = e || t.length > i ? t.slice(e, e + i) : t, s ? tt.call(this, t) : t;
  let n = [];
  for (let r = 0, h, o; r < t.length; r++) if ((h = t[r]) && (o = h.length)) {
    if (e) {
      if (e >= o) {
        e -= o;
        continue;
      }
      h = h.slice(e, e + i), o = h.length, e = 0;
    }
    if (o > i && (h = h.slice(0, i), o = i), !n.length && o >= i) return s ? tt.call(this, h) : h;
    if (n.push(h), i -= o, !i) break;
  }
  return n = n.length > 1 ? [].concat.apply([], n) : n[0], s ? tt.call(this, n) : n;
}
function bt(t, i, e, s) {
  var n = s[0];
  if (n[0] && n[0].query) return t[i].apply(t, n);
  if (!(i !== "and" && i !== "not" || t.result.length || t.await || n.suggest)) return s.length > 1 && (n = s[s.length - 1]), (s = n.resolve) ? t.await || t.result : t;
  let r = [], h = 0, o = 0, l, f, u, g, m;
  for (i = 0; i < s.length; i++) if (n = s[i]) {
    var d = void 0;
    if (n.constructor === A) d = n.await || n.result;
    else if (n.then || n.constructor === Array) d = n;
    else {
      h = n.limit || 0, o = n.offset || 0, u = n.suggest, f = n.resolve, l = ((g = n.highlight || t.highlight) || n.enrich) && f, d = n.queue;
      let a = n.async || d, c = n.index, p = n.query;
      if (c ? t.index || (t.index = c) : c = t.index, p || n.tag) {
        const x = n.field || n.pluck;
        if (x && (!p || t.query && !g || (t.query = p, t.field = x, t.highlight = g), c = c.index.get(x)), d && (m || t.await)) {
          m = 1;
          let w;
          const b = t.C.length, _ = new Promise(function(z) {
            w = z;
          });
          (function(z, S) {
            _.h = function() {
              S.index = null, S.resolve = !1;
              let j = a ? z.searchAsync(S) : z.search(S);
              return j.then ? j.then(function(k) {
                return t.C[b] = k = k.result || k, w(k), k;
              }) : (j = j.result || j, w(j), j);
            };
          })(c, Object.assign({}, n)), t.C.push(_), r[i] = _;
          continue;
        } else n.resolve = !1, n.index = null, d = a ? c.searchAsync(n) : c.search(n), n.resolve = f, n.index = c;
      } else if (n.and) d = dt(n, "and", c);
      else if (n.or) d = dt(n, "or", c);
      else if (n.not) d = dt(n, "not", c);
      else if (n.xor) d = dt(n, "xor", c);
      else continue;
    }
    d.await ? (m = 1, d = d.await) : d.then ? (m = 1, d = d.then(function(a) {
      return a.result || a;
    })) : d = d.result || d, r[i] = d;
  }
  if (m && !t.await && (t.await = new Promise(function(a) {
    t.return = a;
  })), m) {
    const a = Promise.all(r).then(function(c) {
      for (let p = 0; p < t.C.length; p++) if (t.C[p] === a) {
        t.C[p] = function() {
          return e.call(t, c, h, o, l, f, u, g);
        };
        break;
      }
      Tt(t);
    });
    t.C.push(a);
  } else if (t.await) t.C.push(function() {
    return e.call(t, r, h, o, l, f, u, g);
  });
  else return e.call(t, r, h, o, l, f, u, g);
  return f ? t.await || t.result : t;
}
function dt(t, i, e) {
  t = t[i];
  const s = t[0] || t;
  return s.index || (s.index = e), e = new A(s), t.length > 1 && (e = e[i].apply(e, t.slice(1))), e;
}
A.prototype.or = function() {
  return bt(this, "or", me, arguments);
};
function me(t, i, e, s, n, r, h) {
  return t.length && (this.result.length && t.push(this.result), t.length < 2 ? this.result = t[0] : (this.result = ee(t, i, e, !1, this.h), e = 0)), n && (this.await = null), n ? this.resolve(i, e, s, h) : this;
}
A.prototype.and = function() {
  return bt(this, "and", we, arguments);
};
function we(t, i, e, s, n, r, h) {
  if (!r && !this.result.length) return n ? this.result : this;
  let o;
  if (t.length) if (this.result.length && t.unshift(this.result), t.length < 2) this.result = t[0];
  else {
    let l = 0;
    for (let f = 0, u, g; f < t.length; f++) if ((u = t[f]) && (g = u.length)) l < g && (l = g);
    else if (!r) {
      l = 0;
      break;
    }
    l ? (this.result = yt(t, l, i, e, r, this.h, n), o = !0) : this.result = [];
  }
  else r || (this.result = t);
  return n && (this.await = null), n ? this.resolve(i, e, s, h, o) : this;
}
A.prototype.xor = function() {
  return bt(this, "xor", ye, arguments);
};
function ye(t, i, e, s, n, r, h) {
  if (t.length) if (this.result.length && t.unshift(this.result), t.length < 2) this.result = t[0];
  else {
    t: {
      r = e;
      var o = this.h;
      const l = [], f = I();
      let u = 0;
      for (let g = 0, m; g < t.length; g++) if (m = t[g]) {
        u < m.length && (u = m.length);
        for (let d = 0, a; d < m.length; d++) if (a = m[d]) for (let c = 0, p; c < a.length; c++) p = a[c], f[p] = f[p] ? 2 : 1;
      }
      for (let g = 0, m, d = 0; g < u; g++) for (let a = 0, c; a < t.length; a++) if ((c = t[a]) && (m = c[g])) {
        for (let p = 0, x; p < m.length; p++) if (x = m[p], f[x] === 1) if (r) r--;
        else if (n) {
          if (l.push(x), l.length === i) {
            t = l;
            break t;
          }
        } else {
          const w = g + (a ? o : 0);
          if (l[w] || (l[w] = []), l[w].push(x), ++d === i) {
            t = l;
            break t;
          }
        }
      }
      t = l;
    }
    this.result = t, o = !0;
  }
  else r || (this.result = t);
  return n && (this.await = null), n ? this.resolve(i, e, s, h, o) : this;
}
A.prototype.not = function() {
  return bt(this, "not", xe, arguments);
};
function xe(t, i, e, s, n, r, h) {
  if (!r && !this.result.length) return n ? this.result : this;
  if (t.length && this.result.length) {
    t: {
      r = e;
      var o = [];
      t = new Set(t.flat().flat());
      for (let l = 0, f, u = 0; l < this.result.length; l++) if (f = this.result[l]) {
        for (let g = 0, m; g < f.length; g++) if (m = f[g], !t.has(m)) {
          if (r) r--;
          else if (n) {
            if (o.push(m), o.length === i) {
              t = o;
              break t;
            }
          } else if (o[l] || (o[l] = []), o[l].push(m), ++u === i) {
            t = o;
            break t;
          }
        }
      }
      t = o;
    }
    this.result = t, o = !0;
  }
  return n && (this.await = null), n ? this.resolve(i, e, s, h, o) : this;
}
function wt(t, i, e, s, n) {
  let r, h, o;
  typeof n == "string" ? (r = n, n = "") : r = n.template, h = r.indexOf("$1"), o = r.substring(h + 2), h = r.substring(0, h);
  let l = n && n.boundary, f = !n || n.clip !== !1, u = n && n.merge && o && h && new RegExp(o + " " + h, "g");
  n = n && n.ellipsis;
  var g = 0;
  if (typeof n == "object") {
    var m = n.template;
    g = m.length - 2, n = n.pattern;
  }
  typeof n != "string" && (n = n === !1 ? "" : "..."), g && (n = m.replace("$1", n)), m = n.length - g;
  let d, a;
  typeof l == "object" && (d = l.before, d === 0 && (d = -1), a = l.after, a === 0 && (a = -1), l = l.total || 9e5), g = /* @__PURE__ */ new Map();
  for (let jt = 0, L, Ht, st; jt < i.length; jt++) {
    let rt;
    if (s) rt = i, st = s;
    else {
      var c = i[jt];
      if (st = c.field, !st) continue;
      rt = c.result;
    }
    Ht = e.get(st), L = Ht.encoder, c = g.get(L), typeof c != "string" && (c = L.encode(t), g.set(L, c));
    for (let ct = 0; ct < rt.length; ct++) {
      var p = rt[ct].doc;
      if (!p || (p = ot(p, st), !p)) continue;
      var x = p.trim().split(/\s+/);
      if (!x.length) continue;
      p = "";
      var w = [];
      let gt = [];
      for (var b = -1, _ = -1, z = 0, S = 0; S < x.length; S++) {
        var j = x[S], k = L.encode(j);
        k = k.length > 1 ? k.join(" ") : k[0];
        let v;
        if (k && j) {
          for (var M = j.length, C = (L.split ? j.replace(L.split, "") : j).length - k.length, B = "", $ = 0, T = 0; T < c.length; T++) {
            var K = c[T];
            if (K) {
              var P = K.length;
              P += C < 0 ? 0 : C, $ && P <= $ || (K = k.indexOf(K), K > -1 && (B = (K ? j.substring(0, K) : "") + h + j.substring(K, K + P) + o + (K + P < M ? j.substring(K + P) : ""), $ = P, v = !0));
            }
          }
          B && (l && (b < 0 && (b = p.length + (p ? 1 : 0)), _ = p.length + (p ? 1 : 0) + B.length, z += M, gt.push(w.length), w.push({ match: B })), p += (p ? " " : "") + B);
        }
        if (!v) j = x[S], p += (p ? " " : "") + j, l && w.push({ text: j });
        else if (l && z >= l) break;
      }
      if (z = gt.length * (r.length - 2), d || a || l && p.length - z > l) if (z = l + z - m * 2, S = _ - b, d > 0 && (S += d), a > 0 && (S += a), S <= z) x = d ? b - (d > 0 ? d : 0) : b - ((z - S) / 2 | 0), w = a ? _ + (a > 0 ? a : 0) : x + z, f || (x > 0 && p.charAt(x) !== " " && p.charAt(x - 1) !== " " && (x = p.indexOf(" ", x), x < 0 && (x = 0)), w < p.length && p.charAt(w - 1) !== " " && p.charAt(w) !== " " && (w = p.lastIndexOf(" ", w), w < _ ? w = _ : ++w)), p = (x ? n : "") + p.substring(x, w) + (w < p.length ? n : "");
      else {
        for (_ = [], b = {}, z = {}, S = {}, j = {}, k = {}, B = C = M = 0, T = $ = 1; ; ) {
          var Z = void 0;
          for (let v = 0, O; v < gt.length; v++) {
            if (O = gt[v], B) if (C !== B) {
              if (S[v + 1]) continue;
              if (O += B, b[O]) {
                M -= m, z[v + 1] = 1, S[v + 1] = 1;
                continue;
              }
              if (O >= w.length - 1) {
                if (O >= w.length) {
                  S[v + 1] = 1, O >= x.length && (z[v + 1] = 1);
                  continue;
                }
                M -= m;
              }
              if (p = w[O].text, P = a && k[v]) if (P > 0) {
                if (p.length > P) if (S[v + 1] = 1, f) p = p.substring(0, P);
                else continue;
                (P -= p.length) || (P = -1), k[v] = P;
              } else {
                S[v + 1] = 1;
                continue;
              }
              if (M + p.length + 1 <= l) p = " " + p, _[v] += p;
              else if (f) Z = l - M - 1, Z > 0 && (p = " " + p.substring(0, Z), _[v] += p), S[v + 1] = 1;
              else {
                S[v + 1] = 1;
                continue;
              }
            } else {
              if (S[v]) continue;
              if (O -= C, b[O]) {
                M -= m, S[v] = 1, z[v] = 1;
                continue;
              }
              if (O <= 0) {
                if (O < 0) {
                  S[v] = 1, z[v] = 1;
                  continue;
                }
                M -= m;
              }
              if (p = w[O].text, P = d && j[v]) if (P > 0) {
                if (p.length > P) if (S[v] = 1, f) p = p.substring(p.length - P);
                else continue;
                (P -= p.length) || (P = -1), j[v] = P;
              } else {
                S[v] = 1;
                continue;
              }
              if (M + p.length + 1 <= l) p += " ", _[v] = p + _[v];
              else if (f) Z = p.length + 1 - (l - M), Z >= 0 && Z < p.length && (p = p.substring(Z) + " ", _[v] = p + _[v]), S[v] = 1;
              else {
                S[v] = 1;
                continue;
              }
            }
            else {
              p = w[O].match, d && (j[v] = d), a && (k[v] = a), v && M++;
              let Mt;
              if (O ? !v && m && (M += m) : (z[v] = 1, S[v] = 1), O >= x.length - 1 || O < w.length - 1 && w[O + 1].match ? Mt = 1 : m && (M += m), M -= r.length - 2, !v || M + p.length <= l) _[v] = p;
              else {
                Z = $ = T = z[v] = 0;
                break;
              }
              Mt && (z[v + 1] = 1, S[v + 1] = 1);
            }
            M += p.length, Z = b[O] = 1;
          }
          if (Z) C === B ? B++ : C++;
          else {
            if (C === B ? $ = 0 : T = 0, !$ && !T) break;
            $ ? (C++, B = C) : B++;
          }
        }
        p = "";
        for (let v = 0, O; v < _.length; v++) O = (z[v] ? v ? " " : "" : (v && !n ? " " : "") + n) + _[v], p += O;
        n && !z[_.length] && (p += n);
      }
      u && (p = p.replace(u, " ")), rt[ct].highlight = p;
    }
    if (s) break;
  }
  return i;
}
function A(t, i) {
  if (!this || this.constructor !== A) return new A(t, i);
  let e = 0, s, n, r, h, o, l;
  if (t && t.index) {
    const f = t;
    if (i = f.index, e = f.boost || 0, n = f.query) {
      r = f.field || f.pluck, h = f.highlight;
      const u = f.resolve;
      t = f.async || f.queue, f.resolve = !1, f.index = null, t = t ? i.searchAsync(f) : i.search(f), f.resolve = u, f.index = i, t = t.result || t;
    } else t = [];
  }
  if (t && t.then) {
    const f = this;
    t = t.then(function(u) {
      f.C[0] = f.result = u.result || u, Tt(f);
    }), s = [t], t = [], o = new Promise(function(u) {
      l = u;
    });
  }
  this.index = i || null, this.result = t || [], this.h = e, this.C = s || [], this.await = o || null, this.return = l || null, this.highlight = h || null, this.query = n || "", this.field = r || "";
}
y = A.prototype;
y.limit = function(t) {
  if (this.await) {
    const i = this;
    this.C.push(function() {
      return i.limit(t).result;
    });
  } else if (this.result.length) {
    const i = [];
    for (let e = 0, s; e < this.result.length; e++) if (s = this.result[e]) if (s.length <= t) {
      if (i[e] = s, t -= s.length, !t) break;
    } else {
      i[e] = s.slice(0, t);
      break;
    }
    this.result = i;
  }
  return this;
};
y.offset = function(t) {
  if (this.await) {
    const i = this;
    this.C.push(function() {
      return i.offset(t).result;
    });
  } else if (this.result.length) {
    const i = [];
    for (let e = 0, s; e < this.result.length; e++) (s = this.result[e]) && (s.length <= t ? t -= s.length : (i[e] = s.slice(t), t = 0));
    this.result = i;
  }
  return this;
};
y.boost = function(t) {
  if (this.await) {
    const i = this;
    this.C.push(function() {
      return i.boost(t).result;
    });
  } else this.h += t;
  return this;
};
function Tt(t, i) {
  let e = t.result;
  var s = t.await;
  t.await = null;
  for (let n = 0, r; n < t.C.length; n++) if (r = t.C[n]) {
    if (typeof r == "function") e = r(), t.C[n] = e = e.result || e, n--;
    else if (r.h) e = r.h(), t.C[n] = e = e.result || e, n--;
    else if (r.then) return t.await = s;
  }
  return s = t.return, t.C = [], t.return = null, i || s(e), e;
}
y.resolve = function(t, i, e, s, n) {
  let r = this.await ? Tt(this, !0) : this.result;
  if (r.then) {
    const h = this;
    return r.then(function() {
      return h.resolve(t, i, e, s, n);
    });
  }
  return r.length && (typeof t == "object" ? (s = t.highlight || this.highlight, e = !!s || t.enrich, i = t.offset, t = t.limit) : (s = s || this.highlight, e = !!s || e), r = n ? e ? tt.call(this.index, r) : r : Rt.call(this.index, r, t || 100, i, e)), this.finalize(r, s);
};
y.finalize = function(t, i) {
  if (t.then) {
    const s = this;
    return t.then(function(n) {
      return s.finalize(n, i);
    });
  }
  i && t.length && this.query && (t = wt(this.query, t, this.index.index, this.field, i));
  const e = this.return;
  return this.highlight = this.index = this.result = this.C = this.await = this.return = null, this.query = this.field = "", e && e(t), t;
};
function yt(t, i, e, s, n, r, h) {
  const o = t.length;
  let l = [], f, u;
  f = I();
  for (let g = 0, m, d, a, c; g < i; g++) for (let p = 0; p < o; p++) if (a = t[p], g < a.length && (m = a[g])) for (let x = 0; x < m.length; x++) {
    if (d = m[x], (u = f[d]) ? f[d]++ : (u = 0, f[d] = 1), c = l[u] || (l[u] = []), !h) {
      let w = g + (p || !n ? 0 : r || 0);
      c = c[w] || (c[w] = []);
    }
    if (c.push(d), h && e && u === o - 1 && c.length - s === e) return s ? c.slice(s) : c;
  }
  if (t = l.length) if (n) l = l.length > 1 ? ee(l, e, s, h, r) : (l = l[0]) && e && l.length > e || s ? l.slice(s, e + s) : l;
  else {
    if (t < o) return [];
    if (l = l[t - 1], e || s) if (h)
      (l.length > e || s) && (l = l.slice(s, e + s));
    else {
      n = [];
      for (let g = 0, m; g < l.length; g++) if (m = l[g]) {
        if (s && m.length > s) s -= m.length;
        else if ((e && m.length > e || s) && (m = m.slice(s, e + s), e -= m.length, s && (s -= m.length)), n.push(m), !e) break;
      }
      l = n;
    }
  }
  return l;
}
function ee(t, i, e, s, n) {
  const r = [], h = I();
  let o;
  var l = t.length;
  let f;
  if (s) {
    for (n = l - 1; n >= 0; n--)
      if (f = (s = t[n]) && s.length) {
        for (l = 0; l < f; l++) if (o = s[l], !h[o]) {
          if (h[o] = 1, e) e--;
          else if (r.push(o), r.length === i) return r;
        }
      }
  } else for (let u = l - 1, g, m = 0; u >= 0; u--) {
    g = t[u];
    for (let d = 0; d < g.length; d++) if (f = (s = g[d]) && s.length) {
      for (let a = 0; a < f; a++) if (o = s[a], !h[o]) if (h[o] = 1, e) e--;
      else {
        let c = (d + (u < l - 1 && n || 0)) / (u + 1) | 0;
        if ((r[c] || (r[c] = [])).push(o), ++m === i) return r;
      }
    }
  }
  return r;
}
function ke(t, i, e, s, n) {
  const r = I(), h = [];
  for (let o = 0, l; o < i.length; o++) {
    l = i[o];
    for (let f = 0; f < l.length; f++) r[l[f]] = 1;
  }
  if (n) {
    for (let o = 0, l; o < t.length; o++)
      if (l = t[o], r[l]) {
        if (s) s--;
        else if (h.push(l), r[l] = 0, e && --e === 0) break;
      }
  } else for (let o = 0, l, f; o < t.result.length; o++) for (l = t.result[o], i = 0; i < l.length; i++) f = l[i], r[f] && ((h[o] || (h[o] = [])).push(f), r[f] = 0);
  return h;
}
nt.prototype.search = function(t, i, e, s) {
  e || (!i && lt(t) ? (e = t, t = "") : lt(i) && (e = i, i = 0));
  let n = [];
  var r = [];
  let h, o, l, f, u, g, m = 0, d = !0, a;
  if (e) {
    e.constructor === Array && (e = { index: e }), t = e.query || t, h = e.pluck, o = e.merge, f = e.boost, g = h || e.field || (g = e.index) && (g.index ? null : g);
    var c = this.tag && e.tag;
    l = e.suggest, d = e.resolve !== !1, u = e.cache, a = d && this.store && e.highlight;
    var p = !!a || d && this.store && e.enrich;
    i = e.limit || i;
    var x = e.offset || 0;
    if (i || (i = d ? 100 : 0), c && (!this.db || !s)) {
      c.constructor !== Array && (c = [c]);
      var w = [];
      for (let j = 0, k; j < c.length; j++) if (k = c[j], k.field && k.tag) {
        var b = k.tag;
        if (b.constructor === Array) for (var _ = 0; _ < b.length; _++) w.push(k.field, b[_]);
        else w.push(k.field, b);
      } else {
        b = Object.keys(k);
        for (let M = 0, C, B; M < b.length; M++) if (C = b[M], B = k[C], B.constructor === Array) for (_ = 0; _ < B.length; _++) w.push(C, B[_]);
        else w.push(C, B);
      }
      if (c = w, !t) {
        if (r = [], w.length) for (c = 0; c < w.length; c += 2) {
          if (this.db) {
            if (s = this.index.get(w[c]), !s) continue;
            r.push(s = s.db.tag(w[c + 1], i, x, p));
          } else s = ve.call(this, w[c], w[c + 1], i, x, p);
          n.push(d ? { field: w[c], tag: w[c + 1], result: s } : [s]);
        }
        if (r.length) {
          const j = this;
          return Promise.all(r).then(function(k) {
            for (let M = 0; M < k.length; M++) d ? n[M].result = k[M] : n[M] = k[M];
            return d ? n : new A(n.length > 1 ? yt(n, 1, 0, 0, l, f) : n[0], j);
          });
        }
        return d ? n : new A(n.length > 1 ? yt(n, 1, 0, 0, l, f) : n[0], this);
      }
    }
    d || h || !(g = g || this.field) || (N(g) ? h = g : (g.constructor === Array && g.length === 1 && (g = g[0]), h = g.field || g.index)), g && g.constructor !== Array && (g = [g]);
  }
  g || (g = this.field);
  let z;
  w = (this.worker || this.db) && !s && [];
  for (let j = 0, k, M, C; j < g.length; j++) {
    if (M = g[j], this.db && this.tag && !this.B[j]) continue;
    let B;
    if (N(M) || (B = M, M = B.field, t = B.query || t, i = U(B.limit, i), x = U(B.offset, x), l = U(B.suggest, l), a = d && this.store && U(B.highlight, a), p = !!a || d && this.store && U(B.enrich, p), u = U(B.cache, u)), s) k = s[j];
    else {
      b = B || e || {}, _ = b.enrich;
      var S = this.index.get(M);
      if (c && (this.db && (b.tag = c, b.field = g, z = S.db.support_tag_search), !z && _ && (b.enrich = !1), z || (b.limit = 0, b.offset = 0)), k = u ? S.searchCache(t, c && !z ? 0 : i, b) : S.search(t, c && !z ? 0 : i, b), c && !z && (b.limit = i, b.offset = x), _ && (b.enrich = _), w) {
        w[j] = k;
        continue;
      }
    }
    if (C = (k = k.result || k) && k.length, c && C) {
      if (b = [], _ = 0, this.db && s) {
        if (!z) for (S = g.length; S < s.length; S++) {
          let $ = s[S];
          if ($ && $.length) _++, b.push($);
          else if (!l) return d ? n : new A(n, this);
        }
      } else for (let $ = 0, T, K; $ < c.length; $ += 2) {
        if (T = this.tag.get(c[$]), !T) {
          if (l) continue;
          return d ? n : new A(n, this);
        }
        if (K = (T = T && T.get(c[$ + 1])) && T.length) _++, b.push(T);
        else if (!l) return d ? n : new A(n, this);
      }
      if (_) {
        if (k = ke(k, b, i, x, d), C = k.length, !C && !l) return d ? k : new A(k, this);
        _--;
      }
    }
    if (C) r[m] = M, n.push(k), m++;
    else if (g.length === 1) return d ? n : new A(
      n,
      this
    );
  }
  if (w) {
    if (this.db && c && c.length && !z) for (p = 0; p < c.length; p += 2) {
      if (r = this.index.get(c[p]), !r) {
        if (l) continue;
        return d ? n : new A(n, this);
      }
      w.push(r.db.tag(c[p + 1], i, x, !1));
    }
    const j = this;
    return Promise.all(w).then(function(k) {
      return e && (e.resolve = d), k.length && (k = j.search(t, i, e, k)), k;
    });
  }
  if (!m) return d ? n : new A(n, this);
  if (h && (!p || !this.store)) return n = n[0], d ? n : new A(n, this);
  for (w = [], x = 0; x < r.length; x++) {
    if (c = n[x], p && c.length && typeof c[0].doc > "u" && (this.db ? w.push(c = this.index.get(this.field[0]).db.enrich(c)) : c = tt.call(this, c)), h) return d ? a ? wt(t, c, this.index, h, a) : c : new A(c, this);
    n[x] = { field: r[x], result: c };
  }
  if (p && this.db && w.length) {
    const j = this;
    return Promise.all(w).then(function(k) {
      for (let M = 0; M < k.length; M++) n[M].result = k[M];
      return a && (n = wt(t, n, j.index, h, a)), o ? Lt(n) : n;
    });
  }
  return a && (n = wt(t, n, this.index, h, a)), o ? Lt(n) : n;
};
function Lt(t) {
  const i = [], e = I(), s = I();
  for (let n = 0, r, h, o, l, f, u, g; n < t.length; n++) {
    r = t[n], h = r.field, o = r.result;
    for (let m = 0; m < o.length; m++) f = o[m], typeof f != "object" ? f = { id: l = f } : l = f.id, (u = e[l]) ? u.push(h) : (f.field = e[l] = [h], i.push(f)), (g = f.highlight) && (u = s[l], u || (s[l] = u = {}, f.highlight = u), u[h] = g);
  }
  return i;
}
function ve(t, i, e, s, n) {
  return t = this.tag.get(t), t ? (t = t.get(i), t ? (i = t.length - s, i > 0 && ((e && i > e || s) && (t = t.slice(s, s + e)), n && (t = tt.call(this, t))), t) : []) : [];
}
function tt(t) {
  if (!this || !this.store) return t;
  if (this.db) return this.index.get(this.field[0]).db.enrich(t);
  const i = Array(t.length);
  for (let e = 0, s; e < t.length; e++) s = t[e], i[e] = { id: s, doc: this.store.get(s) };
  return i;
}
function nt(t) {
  if (!this || this.constructor !== nt) return new nt(t);
  const i = t.document || t.doc || t;
  let e, s;
  if (this.B = [], this.field = [], this.D = [], this.key = (e = i.key || i.id) && xt(e, this.D) || "id", (s = t.keystore || 0) && (this.keystore = s), this.fastupdate = !!t.fastupdate, this.reg = !this.fastupdate || t.worker || t.db ? s ? new W(s) : /* @__PURE__ */ new Set() : s ? new H(s) : /* @__PURE__ */ new Map(), this.h = (e = i.store || null) && e && e !== !0 && [], this.store = e ? s ? new H(s) : /* @__PURE__ */ new Map() : null, this.cache = (e = t.cache || null) && new G(e), t.cache = !1, this.worker = t.worker || !1, this.priority = t.priority || 4, this.index = be.call(this, t, i), this.tag = null, (e = i.tag) && (typeof e == "string" && (e = [e]), e.length)) {
    this.tag = /* @__PURE__ */ new Map(), this.A = [], this.F = [];
    for (let n = 0, r, h; n < e.length; n++) {
      if (r = e[n], h = r.field || r, !h) throw Error("The tag field from the document descriptor is undefined.");
      r.custom ? this.A[n] = r.custom : (this.A[n] = xt(h, this.D), r.filter && (typeof this.A[n] == "string" && (this.A[n] = new String(this.A[n])), this.A[n].G = r.filter)), this.F[n] = h, this.tag.set(h, /* @__PURE__ */ new Map());
    }
  }
  if (this.worker) {
    this.fastupdate = !1, t = [];
    for (const n of this.index.values()) n.then && t.push(n);
    if (t.length) {
      const n = this;
      return Promise.all(t).then(function(r) {
        let h = 0;
        for (const o of n.index.entries()) {
          const l = o[0];
          let f = o[1];
          f.then && (f = r[h], n.index.set(l, f), h++);
        }
        return n;
      });
    }
  } else t.db && (this.fastupdate = !1, this.mount(t.db));
}
y = nt.prototype;
y.mount = function(t) {
  let i = this.field;
  if (this.tag) for (let r = 0, h; r < this.F.length; r++) {
    h = this.F[r];
    var e = void 0;
    this.index.set(h, e = new J({}, this.reg)), i === this.field && (i = i.slice(0)), i.push(h), e.tag = this.tag.get(h);
  }
  e = [];
  const s = { db: t.db, type: t.type, fastupdate: t.fastupdate };
  for (let r = 0, h, o; r < i.length; r++) {
    s.field = o = i[r], h = this.index.get(o);
    const l = new t.constructor(t.id, s);
    l.id = t.id, e[r] = l.mount(h), h.document = !0, r ? h.bypass = !0 : h.store = this.store;
  }
  const n = this;
  return this.db = Promise.all(e).then(function() {
    n.db = !0;
  });
};
y.commit = async function() {
  const t = [];
  for (const i of this.index.values()) t.push(i.commit());
  await Promise.all(t), this.reg.clear();
};
y.destroy = function() {
  const t = [];
  for (const i of this.index.values()) t.push(i.destroy());
  return Promise.all(t);
};
function be(t, i) {
  const e = /* @__PURE__ */ new Map();
  let s = i.index || i.field || i;
  N(s) && (s = [s]);
  for (let r = 0, h, o; r < s.length; r++) {
    if (h = s[r], N(h) || (o = h, h = h.field), o = lt(o) ? Object.assign({}, t, o) : t, this.worker) {
      var n = void 0;
      n = (n = o.encoder) && n.encode ? n : new ft(typeof n == "string" ? Et[n] : n || {}), n = new it(o, n), e.set(h, n);
    }
    this.worker || e.set(h, new J(o, this.reg)), o.custom ? this.B[r] = o.custom : (this.B[r] = xt(h, this.D), o.filter && (typeof this.B[r] == "string" && (this.B[r] = new String(this.B[r])), this.B[r].G = o.filter)), this.field[r] = h;
  }
  if (this.h) {
    t = i.store, N(t) && (t = [t]);
    for (let r = 0, h, o; r < t.length; r++) h = t[r], o = h.field || h, h.custom ? (this.h[r] = h.custom, h.custom.O = o) : (this.h[r] = xt(o, this.D), h.filter && (typeof this.h[r] == "string" && (this.h[r] = new String(this.h[r])), this.h[r].G = h.filter));
  }
  return e;
}
function xt(t, i) {
  const e = t.split(":");
  let s = 0;
  for (let n = 0; n < e.length; n++) t = e[n], t[t.length - 1] === "]" && (t = t.substring(0, t.length - 2)) && (i[s] = !0), t && (e[s++] = t);
  return s < e.length && (e.length = s), s > 1 ? e : e[0];
}
y.append = function(t, i) {
  return this.add(t, i, !0);
};
y.update = function(t, i) {
  return this.remove(t).add(t, i);
};
y.remove = function(t) {
  lt(t) && (t = ot(t, this.key));
  for (var i of this.index.values()) i.remove(t, !0);
  if (this.reg.has(t)) {
    if (this.tag && !this.fastupdate) for (let e of this.tag.values()) for (let s of e) {
      i = s[0];
      const n = s[1], r = n.indexOf(t);
      r > -1 && (n.length > 1 ? n.splice(r, 1) : e.delete(i));
    }
    this.store && this.store.delete(t), this.reg.delete(t);
  }
  return this.cache && this.cache.remove(t), this;
};
y.clear = function() {
  const t = [];
  for (const i of this.index.values()) {
    const e = i.clear();
    e.then && t.push(e);
  }
  if (this.tag) for (const i of this.tag.values()) i.clear();
  return this.store && this.store.clear(), this.cache && this.cache.clear(), t.length ? Promise.all(t) : this;
};
y.contain = function(t) {
  return this.db ? this.index.get(this.field[0]).db.has(t) : this.reg.has(t);
};
y.cleanup = function() {
  for (const t of this.index.values()) t.cleanup();
  return this;
};
y.get = function(t) {
  return this.db ? this.index.get(this.field[0]).db.enrich(t).then(function(i) {
    return i[0] && i[0].doc || null;
  }) : this.store.get(t) || null;
};
y.set = function(t, i) {
  return typeof t == "object" && (i = t, t = ot(i, this.key)), this.store.set(t, i), this;
};
y.searchCache = Pt;
y.export = je;
y.import = Me;
$t(nt.prototype);
function Kt(t, i = 0) {
  let e = [], s = [];
  i && (i = 25e4 / i * 5e3 | 0);
  for (const n of t.entries()) s.push(n), s.length === i && (e.push(s), s = []);
  return s.length && e.push(s), e;
}
function Nt(t, i) {
  i || (i = /* @__PURE__ */ new Map());
  for (let e = 0, s; e < t.length; e++) s = t[e], i.set(s[0], s[1]);
  return i;
}
function ie(t, i = 0) {
  let e = [], s = [];
  i && (i = 25e4 / i * 1e3 | 0);
  for (const n of t.entries()) s.push([n[0], Kt(n[1])[0] || []]), s.length === i && (e.push(s), s = []);
  return s.length && e.push(s), e;
}
function ne(t, i) {
  i || (i = /* @__PURE__ */ new Map());
  for (let e = 0, s, n; e < t.length; e++) s = t[e], n = i.get(s[0]), i.set(s[0], Nt(s[1], n));
  return i;
}
function se(t) {
  let i = [], e = [];
  for (const s of t.keys()) e.push(s), e.length === 25e4 && (i.push(e), e = []);
  return e.length && i.push(e), i;
}
function re(t, i) {
  i || (i = /* @__PURE__ */ new Set());
  for (let e = 0; e < t.length; e++) i.add(t[e]);
  return i;
}
function kt(t, i, e, s, n, r, h = 0) {
  const o = s && s.constructor === Array;
  var l = o ? s.shift() : s;
  if (!l) return this.export(t, i, n, r + 1);
  if ((l = t((i ? i + "." : "") + (h + 1) + "." + e, JSON.stringify(l))) && l.then) {
    const f = this;
    return l.then(function() {
      return kt.call(f, t, i, e, o ? s : null, n, r, h + 1);
    });
  }
  return kt.call(this, t, i, e, o ? s : null, n, r, h + 1);
}
function je(t, i, e = 0, s = 0) {
  if (e < this.field.length) {
    const h = this.field[e];
    if ((i = this.index.get(h).export(t, h, e, s = 1)) && i.then) {
      const o = this;
      return i.then(function() {
        return o.export(t, h, e + 1);
      });
    }
    return this.export(t, h, e + 1);
  }
  let n, r;
  switch (s) {
    case 0:
      n = "reg", r = se(this.reg), i = null;
      break;
    case 1:
      n = "tag", r = this.tag && ie(this.tag, this.reg.size), i = null;
      break;
    case 2:
      n = "doc", r = this.store && Kt(this.store), i = null;
      break;
    default:
      return;
  }
  return kt.call(this, t, i, n, r || null, e, s);
}
function Me(t, i) {
  var e = t.split(".");
  e[e.length - 1] === "json" && e.pop();
  const s = e.length > 2 ? e[0] : "";
  if (e = e.length > 2 ? e[2] : e[1], this.worker && s) return this.index.get(s).import(t);
  if (i) {
    if (typeof i == "string" && (i = JSON.parse(i)), s) return this.index.get(s).import(e, i);
    switch (e) {
      case "reg":
        this.fastupdate = !1, this.reg = re(i, this.reg);
        for (let n = 0, r; n < this.field.length; n++) r = this.index.get(this.field[n]), r.fastupdate = !1, r.reg = this.reg;
        if (this.worker) {
          i = [];
          for (const n of this.index.values()) i.push(n.import(t));
          return Promise.all(i);
        }
        break;
      case "tag":
        this.tag = ne(i, this.tag);
        break;
      case "doc":
        this.store = Nt(i, this.store);
    }
  }
}
function Ft(t, i) {
  let e = "";
  for (const s of t.entries()) {
    t = s[0];
    const n = s[1];
    let r = "";
    for (let h = 0, o; h < n.length; h++) {
      o = n[h] || [""];
      let l = "";
      for (let f = 0; f < o.length; f++) l += (l ? "," : "") + (i === "string" ? '"' + o[f] + '"' : o[f]);
      l = "[" + l + "]", r += (r ? "," : "") + l;
    }
    r = '["' + t + '",[' + r + "]]", e += (e ? "," : "") + r;
  }
  return e;
}
J.prototype.remove = function(t, i) {
  const e = this.reg.size && (this.fastupdate ? this.reg.get(t) : this.reg.has(t));
  if (e) {
    if (this.fastupdate) {
      for (let s = 0, n, r; s < e.length; s++)
        if ((n = e[s]) && (r = n.length)) if (n[r - 1] === t) n.pop();
        else {
          const h = n.indexOf(t);
          h >= 0 && n.splice(h, 1);
        }
    } else ut(this.map, t), this.depth && ut(this.ctx, t);
    i || this.reg.delete(t);
  }
  return this.db && (this.commit_task.push({ del: t }), this.M && he(this)), this.cache && this.cache.remove(t), this;
};
function ut(t, i) {
  let e = 0;
  var s = typeof i > "u";
  if (t.constructor === Array) {
    for (let n = 0, r, h, o; n < t.length; n++)
      if ((r = t[n]) && r.length) {
        if (s) return 1;
        if (h = r.indexOf(i), h >= 0) {
          if (r.length > 1) return r.splice(h, 1), 1;
          if (delete t[n], e) return 1;
          o = 1;
        } else {
          if (o) return 1;
          e++;
        }
      }
  } else for (let n of t.entries()) s = n[0], ut(n[1], i) ? e++ : t.delete(s);
  return e;
}
const Se = { memory: { resolution: 1 }, performance: { resolution: 3, fastupdate: !0, context: { depth: 1, resolution: 1 } }, match: { tokenize: "forward" }, score: { resolution: 9, context: { depth: 2, resolution: 3 } } };
J.prototype.add = function(t, i, e, s) {
  if (i && (t || t === 0)) {
    if (!s && !e && this.reg.has(t)) return this.update(t, i);
    s = this.depth, i = this.encoder.encode(i, !s);
    const f = i.length;
    if (f) {
      const u = I(), g = I(), m = this.resolution;
      for (let d = 0; d < f; d++) {
        let a = i[this.rtl ? f - 1 - d : d];
        var n = a.length;
        if (n && (s || !g[a])) {
          var r = this.score ? this.score(i, a, d, null, 0) : at(m, f, d), h = "";
          switch (this.tokenize) {
            case "tolerant":
              if (Q(this, g, a, r, t, e), n > 2) {
                for (let c = 1, p, x, w, b; c < n - 1; c++) p = a.charAt(c), x = a.charAt(c + 1), w = a.substring(0, c) + x, b = a.substring(c + 2), h = w + p + b, Q(this, g, h, r, t, e), h = w + b, Q(this, g, h, r, t, e);
                Q(this, g, a.substring(0, a.length - 1), r, t, e);
              }
              break;
            case "full":
              if (n > 2) {
                for (let c = 0, p; c < n; c++) for (r = n; r > c; r--) {
                  h = a.substring(c, r), p = this.rtl ? n - 1 - c : c;
                  var o = this.score ? this.score(i, a, d, h, p) : at(m, f, d, n, p);
                  Q(this, g, h, o, t, e);
                }
                break;
              }
            case "bidirectional":
            case "reverse":
              if (n > 1) {
                for (o = n - 1; o > 0; o--) {
                  h = a[this.rtl ? n - 1 - o : o] + h;
                  var l = this.score ? this.score(i, a, d, h, o) : at(m, f, d, n, o);
                  Q(this, g, h, l, t, e);
                }
                h = "";
              }
            case "forward":
              if (n > 1) {
                for (o = 0; o < n; o++) h += a[this.rtl ? n - 1 - o : o], Q(
                  this,
                  g,
                  h,
                  r,
                  t,
                  e
                );
                break;
              }
            default:
              if (Q(this, g, a, r, t, e), s && f > 1 && d < f - 1) for (n = this.N, h = a, r = Math.min(s + 1, this.rtl ? d + 1 : f - d), o = 1; o < r; o++) {
                a = i[this.rtl ? f - 1 - d - o : d + o], l = this.bidirectional && a > h;
                const c = this.score ? this.score(i, h, d, a, o - 1) : at(n + (f / 2 > n ? 0 : 1), f, d, r - 1, o - 1);
                Q(this, u, l ? h : a, c, t, e, l ? a : h);
              }
          }
        }
      }
      this.fastupdate || this.reg.add(t);
    }
  }
  return this.db && (this.commit_task.push(e ? { ins: t } : { del: t }), this.M && he(this)), this;
};
function Q(t, i, e, s, n, r, h) {
  let o, l;
  if (!(o = i[e]) || h && !o[h]) {
    if (h ? (i = o || (i[e] = I()), i[h] = 1, l = t.ctx, (o = l.get(h)) ? l = o : l.set(h, l = t.keystore ? new H(t.keystore) : /* @__PURE__ */ new Map())) : (l = t.map, i[e] = 1), (o = l.get(e)) ? l = o : l.set(e, l = o = []), r) {
      for (let f = 0, u; f < o.length; f++) if ((u = o[f]) && u.includes(n)) {
        if (f <= s) return;
        u.splice(u.indexOf(n), 1), t.fastupdate && (i = t.reg.get(n)) && i.splice(i.indexOf(u), 1);
        break;
      }
    }
    if (l = l[s] || (l[s] = []), l.push(n), l.length === 2 ** 31 - 1) {
      if (i = new et(l), t.fastupdate) for (let f of t.reg.values()) f.includes(l) && (f[f.indexOf(l)] = i);
      o[s] = l = i;
    }
    t.fastupdate && ((s = t.reg.get(n)) ? s.push(l) : t.reg.set(n, [l]));
  }
}
function at(t, i, e, s, n) {
  return e && t > 1 ? i + (s || 0) <= t ? e + (n || 0) : (t - 1) / (i + (s || 0)) * (e + (n || 0)) + 1 | 0 : 0;
}
J.prototype.search = function(t, i, e) {
  if (e || (i || typeof t != "object" ? typeof i == "object" && (e = i, i = 0) : (e = t, t = "")), e && e.cache) return e.cache = !1, t = this.searchCache(t, i, e), e.cache = !0, t;
  let s = [], n, r, h, o = 0, l, f, u, g, m;
  e && (t = e.query || t, i = e.limit || i, o = e.offset || 0, r = e.context, h = e.suggest, m = (l = e.resolve) && e.enrich, u = e.boost, g = e.resolution, f = this.db && e.tag), typeof l > "u" && (l = this.resolve), r = this.depth && r !== !1;
  let d = this.encoder.encode(t, !r);
  if (n = d.length, i = i || (l ? 100 : 0), n === 1) return Gt.call(
    this,
    d[0],
    "",
    i,
    o,
    l,
    m,
    f
  );
  if (n === 2 && r && !h) return Gt.call(this, d[1], d[0], i, o, l, m, f);
  let a = I(), c = 0, p;
  if (r && (p = d[0], c = 1), g || g === 0 || (g = p ? this.N : this.resolution), this.db) {
    if (this.db.search && (e = this.db.search(this, d, i, o, h, l, m, f), e !== !1)) return e;
    const x = this;
    return (async function() {
      for (let w, b; c < n; c++) {
        if ((b = d[c]) && !a[b]) {
          if (a[b] = 1, w = await Ot(x, b, p, 0, 0, !1, !1), w = Ut(w, s, h, g)) {
            s = w;
            break;
          }
          p && (h && w && s.length || (p = b));
        }
        h && p && c === n - 1 && !s.length && (g = x.resolution, p = "", c = -1, a = I());
      }
      return Dt(s, g, i, o, h, u, l);
    })();
  }
  for (let x, w; c < n; c++) {
    if ((w = d[c]) && !a[w]) {
      if (a[w] = 1, x = Ot(this, w, p, 0, 0, !1, !1), x = Ut(x, s, h, g)) {
        s = x;
        break;
      }
      p && (h && x && s.length || (p = w));
    }
    h && p && c === n - 1 && !s.length && (g = this.resolution, p = "", c = -1, a = I());
  }
  return Dt(s, g, i, o, h, u, l);
};
function Dt(t, i, e, s, n, r, h) {
  let o = t.length, l = t;
  if (o > 1) l = yt(t, i, e, s, n, r, h);
  else if (o === 1) return h ? Rt.call(null, t[0], e, s) : new A(t[0], this);
  return h ? l : new A(l, this);
}
function Gt(t, i, e, s, n, r, h) {
  return t = Ot(this, t, i, e, s, n, r, h), this.db ? t.then(function(o) {
    return n ? o || [] : new A(o, this);
  }) : t && t.length ? n ? Rt.call(this, t, e, s) : new A(t, this) : n ? [] : new A([], this);
}
function Ut(t, i, e, s) {
  let n = [];
  if (t && t.length) {
    if (t.length <= s) {
      i.push(t);
      return;
    }
    for (let r = 0, h; r < s; r++) (h = t[r]) && (n[r] = h);
    if (n.length) {
      i.push(n);
      return;
    }
  }
  if (!e) return n;
}
function Ot(t, i, e, s, n, r, h, o) {
  let l;
  return e && (l = t.bidirectional && i > e) && (l = e, e = i, i = l), t.db ? t.db.get(i, e, s, n, r, h, o) : (t = e ? (t = t.ctx.get(e)) && t.get(i) : t.map.get(i), t);
}
function J(t, i) {
  if (!this || this.constructor !== J) return new J(t);
  if (t) {
    var e = N(t) ? t : t.preset;
    e && (t = Object.assign({}, Se[e], t));
  } else t = {};
  e = t.context;
  const s = e === !0 ? { depth: 1 } : e || {}, n = N(t.encoder) ? Et[t.encoder] : t.encode || t.encoder || {};
  this.encoder = n.encode ? n : typeof n == "object" ? new ft(n) : { encode: n }, this.resolution = t.resolution || 9, this.tokenize = e = (e = t.tokenize) && e !== "default" && e !== "exact" && e || "strict", this.depth = e === "strict" && s.depth || 0, this.bidirectional = s.bidirectional !== !1, this.fastupdate = !!t.fastupdate, this.score = t.score || null, (e = t.keystore || 0) && (this.keystore = e), this.map = e ? new H(e) : /* @__PURE__ */ new Map(), this.ctx = e ? new H(e) : /* @__PURE__ */ new Map(), this.reg = i || (this.fastupdate ? e ? new H(e) : /* @__PURE__ */ new Map() : e ? new W(e) : /* @__PURE__ */ new Set()), this.N = s.resolution || 3, this.rtl = n.rtl || t.rtl || !1, this.cache = (e = t.cache || null) && new G(e), this.resolve = t.resolve !== !1, (e = t.db) && (this.db = this.mount(e)), this.M = t.commit !== !1, this.commit_task = [], this.commit_timer = null, this.priority = t.priority || 4;
}
y = J.prototype;
y.mount = function(t) {
  return this.commit_timer && (clearTimeout(this.commit_timer), this.commit_timer = null), t.mount(this);
};
y.commit = function() {
  return this.commit_timer && (clearTimeout(this.commit_timer), this.commit_timer = null), this.db.commit(this);
};
y.destroy = function() {
  return this.commit_timer && (clearTimeout(this.commit_timer), this.commit_timer = null), this.db.destroy();
};
function he(t) {
  t.commit_timer || (t.commit_timer = setTimeout(function() {
    t.commit_timer = null, t.db.commit(t);
  }, 1));
}
y.clear = function() {
  return this.map.clear(), this.ctx.clear(), this.reg.clear(), this.cache && this.cache.clear(), this.db ? (this.commit_timer && clearTimeout(this.commit_timer), this.commit_timer = null, this.commit_task = [], this.db.clear()) : this;
};
y.append = function(t, i) {
  return this.add(t, i, !0);
};
y.contain = function(t) {
  return this.db ? this.db.has(t) : this.reg.has(t);
};
y.update = function(t, i) {
  const e = this, s = this.remove(t);
  return s && s.then ? s.then(() => e.add(t, i)) : this.add(t, i);
};
y.cleanup = function() {
  return this.fastupdate ? (ut(this.map), this.depth && ut(this.ctx), this) : this;
};
y.searchCache = Pt;
y.export = function(t, i, e = 0, s = 0) {
  let n, r;
  switch (s) {
    case 0:
      n = "reg", r = se(this.reg);
      break;
    case 1:
      n = "cfg", r = null;
      break;
    case 2:
      n = "map", r = Kt(this.map, this.reg.size);
      break;
    case 3:
      n = "ctx", r = ie(this.ctx, this.reg.size);
      break;
    default:
      return;
  }
  return kt.call(this, t, i, n, r, e, s);
};
y.import = function(t, i) {
  if (i) switch (typeof i == "string" && (i = JSON.parse(i)), t = t.split("."), t[t.length - 1] === "json" && t.pop(), t.length === 3 && t.shift(), t = t.length > 1 ? t[1] : t[0], t) {
    case "reg":
      this.fastupdate = !1, this.reg = re(i, this.reg);
      break;
    case "map":
      this.map = Nt(i, this.map);
      break;
    case "ctx":
      this.ctx = ne(i, this.ctx);
  }
};
y.serialize = function(t = !0) {
  let i = "", e = "", s = "";
  if (this.reg.size) {
    let r;
    for (var n of this.reg.keys()) r || (r = typeof n), i += (i ? "," : "") + (r === "string" ? '"' + n + '"' : n);
    i = "index.reg=new Set([" + i + "]);", e = Ft(this.map, r), e = "index.map=new Map([" + e + "]);";
    for (const h of this.ctx.entries()) {
      n = h[0];
      let o = Ft(h[1], r);
      o = "new Map([" + o + "])", o = '["' + n + '",' + o + "]", s += (s ? "," : "") + o;
    }
    s = "index.ctx=new Map([" + s + "]);";
  }
  return t ? "function inject(index){" + i + e + s + "}" : i + e + s;
};
$t(J.prototype);
const le = typeof window < "u" && (window.indexedDB || window.mozIndexedDB || window.webkitIndexedDB || window.msIndexedDB), vt = ["map", "ctx", "tag", "reg", "cfg"], F = I();
function It(t, i = {}) {
  if (!this || this.constructor !== It) return new It(t, i);
  typeof t == "object" && (i = t, t = t.name), t || console.info("Default storage space was used, because a name was not passed."), this.id = "flexsearch" + (t ? ":" + t.toLowerCase().replace(/[^a-z0-9_\-]/g, "") : ""), this.field = i.field ? i.field.toLowerCase().replace(/[^a-z0-9_\-]/g, "") : "", this.type = i.type, this.fastupdate = this.support_tag_search = !1, this.db = null, this.h = {};
}
y = It.prototype;
y.mount = function(t) {
  return t.index ? t.mount(this) : (t.db = this, this.open());
};
y.open = function() {
  if (this.db) return this.db;
  let t = this;
  navigator.storage && navigator.storage.persist && navigator.storage.persist(), F[t.id] || (F[t.id] = []), F[t.id].push(t.field);
  const i = le.open(t.id, 1);
  return i.onupgradeneeded = function() {
    const e = t.db = this.result;
    for (let s = 0, n; s < vt.length; s++) {
      n = vt[s];
      for (let r = 0, h; r < F[t.id].length; r++) h = F[t.id][r], e.objectStoreNames.contains(n + (n !== "reg" && h ? ":" + h : "")) || e.createObjectStore(n + (n !== "reg" && h ? ":" + h : ""));
    }
  }, t.db = Y(i, function(e) {
    t.db = e, t.db.onversionchange = function() {
      t.close();
    };
  });
};
y.close = function() {
  this.db && this.db.close(), this.db = null;
};
y.destroy = function() {
  const t = le.deleteDatabase(this.id);
  return Y(t);
};
y.clear = function() {
  const t = [];
  for (let e = 0, s; e < vt.length; e++) {
    s = vt[e];
    for (let n = 0, r; n < F[this.id].length; n++) r = F[this.id][n], t.push(s + (s !== "reg" && r ? ":" + r : ""));
  }
  const i = this.db.transaction(t, "readwrite");
  for (let e = 0; e < t.length; e++) i.objectStore(t[e]).clear();
  return Y(i);
};
y.get = function(t, i, e = 0, s = 0, n = !0, r = !1) {
  t = this.db.transaction((i ? "ctx" : "map") + (this.field ? ":" + this.field : ""), "readonly").objectStore((i ? "ctx" : "map") + (this.field ? ":" + this.field : "")).get(i ? i + ":" + t : t);
  const h = this;
  return Y(t).then(function(o) {
    let l = [];
    if (!o || !o.length) return l;
    if (n) {
      if (!e && !s && o.length === 1) return o[0];
      for (let f = 0, u; f < o.length; f++) if ((u = o[f]) && u.length) {
        if (s >= u.length) {
          s -= u.length;
          continue;
        }
        const g = e ? s + Math.min(u.length - s, e) : u.length;
        for (let m = s; m < g; m++) l.push(u[m]);
        if (s = 0, l.length === e) break;
      }
      return r ? h.enrich(l) : l;
    }
    return o;
  });
};
y.tag = function(t, i = 0, e = 0, s = !1) {
  t = this.db.transaction("tag" + (this.field ? ":" + this.field : ""), "readonly").objectStore("tag" + (this.field ? ":" + this.field : "")).get(t);
  const n = this;
  return Y(t).then(function(r) {
    return !r || !r.length || e >= r.length ? [] : !i && !e ? r : (r = r.slice(e, e + i), s ? n.enrich(r) : r);
  });
};
y.enrich = function(t) {
  typeof t != "object" && (t = [t]);
  const i = this.db.transaction("reg", "readonly").objectStore("reg"), e = [];
  for (let s = 0; s < t.length; s++) e[s] = Y(i.get(t[s]));
  return Promise.all(e).then(function(s) {
    for (let n = 0; n < s.length; n++) s[n] = { id: t[n], doc: s[n] ? JSON.parse(s[n]) : null };
    return s;
  });
};
y.has = function(t) {
  return t = this.db.transaction("reg", "readonly").objectStore("reg").getKey(t), Y(t).then(function(i) {
    return !!i;
  });
};
y.search = null;
y.info = function() {
};
y.transaction = function(t, i, e) {
  t += t !== "reg" && this.field ? ":" + this.field : "";
  let s = this.h[t + ":" + i];
  if (s) return e.call(this, s);
  let n = this.db.transaction(t, i);
  this.h[t + ":" + i] = s = n.objectStore(t);
  const r = e.call(this, s);
  return this.h[t + ":" + i] = null, Y(n).finally(function() {
    return r;
  });
};
y.commit = async function(t) {
  let i = t.commit_task, e = [];
  t.commit_task = [];
  for (let s = 0, n; s < i.length; s++) n = i[s], n.del && e.push(n.del);
  e.length && await this.remove(e), t.reg.size && (await this.transaction("map", "readwrite", function(s) {
    for (const n of t.map) {
      const r = n[0], h = n[1];
      h.length && (s.get(r).onsuccess = function() {
        let o = this.result;
        var l;
        if (o && o.length) {
          const f = Math.max(o.length, h.length);
          for (let u = 0, g, m; u < f; u++) if ((m = h[u]) && m.length) {
            if ((g = o[u]) && g.length) for (l = 0; l < m.length; l++) g.push(m[l]);
            else o[u] = m;
            l = 1;
          }
        } else o = h, l = 1;
        l && s.put(o, r);
      });
    }
  }), await this.transaction("ctx", "readwrite", function(s) {
    for (const n of t.ctx) {
      const r = n[0], h = n[1];
      for (const o of h) {
        const l = o[0], f = o[1];
        f.length && (s.get(r + ":" + l).onsuccess = function() {
          let u = this.result;
          var g;
          if (u && u.length) {
            const m = Math.max(u.length, f.length);
            for (let d = 0, a, c; d < m; d++) if ((c = f[d]) && c.length) {
              if ((a = u[d]) && a.length) for (g = 0; g < c.length; g++) a.push(c[g]);
              else u[d] = c;
              g = 1;
            }
          } else u = f, g = 1;
          g && s.put(u, r + ":" + l);
        });
      }
    }
  }), t.store ? await this.transaction(
    "reg",
    "readwrite",
    function(s) {
      for (const n of t.store) {
        const r = n[0], h = n[1];
        s.put(typeof h == "object" ? JSON.stringify(h) : 1, r);
      }
    }
  ) : t.bypass || await this.transaction("reg", "readwrite", function(s) {
    for (const n of t.reg.keys()) s.put(1, n);
  }), t.tag && await this.transaction("tag", "readwrite", function(s) {
    for (const n of t.tag) {
      const r = n[0], h = n[1];
      h.length && (s.get(r).onsuccess = function() {
        let o = this.result;
        o = o && o.length ? o.concat(h) : h, s.put(o, r);
      });
    }
  }), t.map.clear(), t.ctx.clear(), t.tag && t.tag.clear(), t.store && t.store.clear(), t.document || t.reg.clear());
};
function _t(t, i, e) {
  const s = t.value;
  let n, r = 0;
  for (let h = 0, o; h < s.length; h++) {
    if (o = e ? s : s[h]) {
      for (let l = 0, f, u; l < i.length; l++) if (u = i[l], f = o.indexOf(u), f >= 0) if (n = 1, o.length > 1) o.splice(f, 1);
      else {
        s[h] = [];
        break;
      }
      r += o.length;
    }
    if (e) break;
  }
  r ? n && t.update(s) : t.delete(), t.continue();
}
y.remove = function(t) {
  return typeof t != "object" && (t = [t]), Promise.all([this.transaction("map", "readwrite", function(i) {
    i.openCursor().onsuccess = function() {
      const e = this.result;
      e && _t(e, t);
    };
  }), this.transaction("ctx", "readwrite", function(i) {
    i.openCursor().onsuccess = function() {
      const e = this.result;
      e && _t(e, t);
    };
  }), this.transaction("tag", "readwrite", function(i) {
    i.openCursor().onsuccess = function() {
      const e = this.result;
      e && _t(e, t, !0);
    };
  }), this.transaction("reg", "readwrite", function(i) {
    for (let e = 0; e < t.length; e++) i.delete(t[e]);
  })]);
};
function Y(t, i) {
  return new Promise((e, s) => {
    t.onsuccess = t.oncomplete = function() {
      i && i(this.result), i = null, e(this.result);
    }, t.onerror = t.onblocked = s, t = null;
  });
}
const oe = J;
let zt = new oe();
self.onmessage = (t) => {
  switch (t.data.type) {
    case "clear":
      zt = new oe(), postMessage({ identifier: t.data.identifier });
      break;
    case "points":
      for (let e of t.data.points)
        zt.add(e.id, e.text);
      postMessage({ identifier: t.data.identifier });
      break;
    case "query":
      let i = zt.search(t.data.query, { limit: t.data.limit });
      postMessage({ identifier: t.data.identifier, result: i });
      break;
  }
};
var _e = /* @__PURE__ */ Object.freeze({
  __proto__: null
});
