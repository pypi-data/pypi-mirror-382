const {
  SvelteComponent: j,
  append_hydration: d,
  attr: f,
  children: v,
  claim_element: u,
  claim_space: g,
  claim_text: q,
  destroy_each: G,
  detach: o,
  element: _,
  empty: k,
  ensure_array_like: E,
  get_svelte_dataset: M,
  init: O,
  insert_hydration: h,
  noop: I,
  safe_not_equal: z,
  set_data: A,
  space: b,
  src_url_equal: p,
  text: P,
  toggle_class: m
} = window.__gradio__svelte__internal;
function D(a, e, i) {
  const s = a.slice();
  return s[3] = e[i], s;
}
function V(a) {
  let e, i, s = E(
    /*value*/
    a[0].slice(0, 3)
  ), l = [];
  for (let n = 0; n < s.length; n += 1)
    l[n] = N(D(a, s, n));
  let t = (
    /*value*/
    a[0].length > 3 && S()
  );
  return {
    c() {
      e = _("div");
      for (let n = 0; n < l.length; n += 1)
        l[n].c();
      i = b(), t && t.c(), this.h();
    },
    l(n) {
      e = u(n, "DIV", { class: !0 });
      var r = v(e);
      for (let c = 0; c < l.length; c += 1)
        l[c].l(r);
      i = g(r), t && t.l(r), r.forEach(o), this.h();
    },
    h() {
      f(e, "class", "images-wrapper svelte-1onbytl");
    },
    m(n, r) {
      h(n, e, r);
      for (let c = 0; c < l.length; c += 1)
        l[c] && l[c].m(e, null);
      d(e, i), t && t.m(e, null);
    },
    p(n, r) {
      if (r & /*value*/
      1) {
        s = E(
          /*value*/
          n[0].slice(0, 3)
        );
        let c;
        for (c = 0; c < s.length; c += 1) {
          const y = D(n, s, c);
          l[c] ? l[c].p(y, r) : (l[c] = N(y), l[c].c(), l[c].m(e, i));
        }
        for (; c < l.length; c += 1)
          l[c].d(1);
        l.length = s.length;
      }
      /*value*/
      n[0].length > 3 ? t || (t = S(), t.c(), t.m(e, null)) : t && (t.d(1), t = null);
    },
    d(n) {
      n && o(e), G(l, n), t && t.d();
    }
  };
}
function B(a) {
  let e, i, s, l, t = (
    /*item*/
    a[3].caption && C(a)
  );
  return {
    c() {
      e = _("div"), i = _("video"), l = b(), t && t.c(), this.h();
    },
    l(n) {
      e = u(n, "DIV", { class: !0 });
      var r = v(e);
      i = u(r, "VIDEO", { src: !0, preload: !0, class: !0 }), v(i).forEach(o), l = g(r), t && t.l(r), r.forEach(o), this.h();
    },
    h() {
      p(i.src, s = /*item*/
      a[3].video.url) || f(i, "src", s), i.controls = !1, i.muted = !0, f(i, "preload", "metadata"), f(i, "class", "svelte-1onbytl"), f(e, "class", "image-container svelte-1onbytl");
    },
    m(n, r) {
      h(n, e, r), d(e, i), d(e, l), t && t.m(e, null);
    },
    p(n, r) {
      r & /*value*/
      1 && !p(i.src, s = /*item*/
      n[3].video.url) && f(i, "src", s), /*item*/
      n[3].caption ? t ? t.p(n, r) : (t = C(n), t.c(), t.m(e, null)) : t && (t.d(1), t = null);
    },
    d(n) {
      n && o(e), t && t.d();
    }
  };
}
function F(a) {
  let e, i, s, l, t, n = (
    /*item*/
    a[3].caption && w(a)
  );
  return {
    c() {
      e = _("div"), i = _("img"), t = b(), n && n.c(), this.h();
    },
    l(r) {
      e = u(r, "DIV", { class: !0 });
      var c = v(e);
      i = u(c, "IMG", { src: !0, alt: !0, class: !0 }), t = g(c), n && n.l(c), c.forEach(o), this.h();
    },
    h() {
      p(i.src, s = /*item*/
      a[3].image.url) || f(i, "src", s), f(i, "alt", l = /*item*/
      a[3].caption || ""), f(i, "class", "svelte-1onbytl"), f(e, "class", "image-container svelte-1onbytl");
    },
    m(r, c) {
      h(r, e, c), d(e, i), d(e, t), n && n.m(e, null);
    },
    p(r, c) {
      c & /*value*/
      1 && !p(i.src, s = /*item*/
      r[3].image.url) && f(i, "src", s), c & /*value*/
      1 && l !== (l = /*item*/
      r[3].caption || "") && f(i, "alt", l), /*item*/
      r[3].caption ? n ? n.p(r, c) : (n = w(r), n.c(), n.m(e, null)) : n && (n.d(1), n = null);
    },
    d(r) {
      r && o(e), n && n.d();
    }
  };
}
function C(a) {
  let e, i = (
    /*item*/
    a[3].caption + ""
  ), s;
  return {
    c() {
      e = _("span"), s = P(i), this.h();
    },
    l(l) {
      e = u(l, "SPAN", { class: !0 });
      var t = v(e);
      s = q(t, i), t.forEach(o), this.h();
    },
    h() {
      f(e, "class", "caption svelte-1onbytl");
    },
    m(l, t) {
      h(l, e, t), d(e, s);
    },
    p(l, t) {
      t & /*value*/
      1 && i !== (i = /*item*/
      l[3].caption + "") && A(s, i);
    },
    d(l) {
      l && o(e);
    }
  };
}
function w(a) {
  let e, i = (
    /*item*/
    a[3].caption + ""
  ), s;
  return {
    c() {
      e = _("span"), s = P(i), this.h();
    },
    l(l) {
      e = u(l, "SPAN", { class: !0 });
      var t = v(e);
      s = q(t, i), t.forEach(o), this.h();
    },
    h() {
      f(e, "class", "caption svelte-1onbytl");
    },
    m(l, t) {
      h(l, e, t), d(e, s);
    },
    p(l, t) {
      t & /*value*/
      1 && i !== (i = /*item*/
      l[3].caption + "") && A(s, i);
    },
    d(l) {
      l && o(e);
    }
  };
}
function N(a) {
  let e;
  function i(t, n) {
    if ("image" in /*item*/
    t[3] && /*item*/
    t[3].image) return F;
    if ("video" in /*item*/
    t[3] && /*item*/
    t[3].video) return B;
  }
  let s = i(a), l = s && s(a);
  return {
    c() {
      l && l.c(), e = k();
    },
    l(t) {
      l && l.l(t), e = k();
    },
    m(t, n) {
      l && l.m(t, n), h(t, e, n);
    },
    p(t, n) {
      s === (s = i(t)) && l ? l.p(t, n) : (l && l.d(1), l = s && s(t), l && (l.c(), l.m(e.parentNode, e)));
    },
    d(t) {
      t && o(e), l && l.d(t);
    }
  };
}
function S(a) {
  let e, i = "…";
  return {
    c() {
      e = _("div"), e.textContent = i, this.h();
    },
    l(s) {
      e = u(s, "DIV", { class: !0, "data-svelte-h": !0 }), M(e) !== "svelte-1u6jrni" && (e.textContent = i), this.h();
    },
    h() {
      f(e, "class", "more-indicator svelte-1onbytl");
    },
    m(s, l) {
      h(s, e, l);
    },
    d(s) {
      s && o(e);
    }
  };
}
function H(a) {
  let e, i = (
    /*value*/
    a[0] && /*value*/
    a[0].length > 0 && V(a)
  );
  return {
    c() {
      e = _("div"), i && i.c(), this.h();
    },
    l(s) {
      e = u(s, "DIV", { class: !0 });
      var l = v(e);
      i && i.l(l), l.forEach(o), this.h();
    },
    h() {
      f(e, "class", "container svelte-1onbytl"), m(
        e,
        "table",
        /*type*/
        a[1] === "table"
      ), m(
        e,
        "gallery",
        /*type*/
        a[1] === "gallery"
      ), m(
        e,
        "selected",
        /*selected*/
        a[2]
      );
    },
    m(s, l) {
      h(s, e, l), i && i.m(e, null);
    },
    p(s, [l]) {
      /*value*/
      s[0] && /*value*/
      s[0].length > 0 ? i ? i.p(s, l) : (i = V(s), i.c(), i.m(e, null)) : i && (i.d(1), i = null), l & /*type*/
      2 && m(
        e,
        "table",
        /*type*/
        s[1] === "table"
      ), l & /*type*/
      2 && m(
        e,
        "gallery",
        /*type*/
        s[1] === "gallery"
      ), l & /*selected*/
      4 && m(
        e,
        "selected",
        /*selected*/
        s[2]
      );
    },
    i: I,
    o: I,
    d(s) {
      s && o(e), i && i.d();
    }
  };
}
function J(a, e, i) {
  let { value: s } = e, { type: l } = e, { selected: t = !1 } = e;
  return a.$$set = (n) => {
    "value" in n && i(0, s = n.value), "type" in n && i(1, l = n.type), "selected" in n && i(2, t = n.selected);
  }, [s, l, t];
}
class K extends j {
  constructor(e) {
    super(), O(this, e, J, H, z, { value: 0, type: 1, selected: 2 });
  }
}
export {
  K as default
};
