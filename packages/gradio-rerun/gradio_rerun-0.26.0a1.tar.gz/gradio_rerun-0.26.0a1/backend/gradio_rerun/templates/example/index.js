const {
  SvelteComponent: g,
  append: v,
  attr: c,
  detach: o,
  element: r,
  empty: y,
  init: b,
  insert: m,
  noop: u,
  safe_not_equal: k,
  src_url_equal: _,
  toggle_class: f
} = window.__gradio__svelte__internal;
function d(a) {
  let l, e, t;
  return {
    c() {
      l = r("div"), e = r("img"), _(e.src, t = /*value*/
      a[0].url) || c(e, "src", t), c(e, "alt", ""), c(e, "class", "svelte-giydt1"), c(l, "class", "container svelte-giydt1"), f(
        l,
        "table",
        /*type*/
        a[1] === "table"
      ), f(
        l,
        "gallery",
        /*type*/
        a[1] === "gallery"
      ), f(
        l,
        "selected",
        /*selected*/
        a[2]
      );
    },
    m(i, n) {
      m(i, l, n), v(l, e);
    },
    p(i, n) {
      n & /*value*/
      1 && !_(e.src, t = /*value*/
      i[0].url) && c(e, "src", t), n & /*type*/
      2 && f(
        l,
        "table",
        /*type*/
        i[1] === "table"
      ), n & /*type*/
      2 && f(
        l,
        "gallery",
        /*type*/
        i[1] === "gallery"
      ), n & /*selected*/
      4 && f(
        l,
        "selected",
        /*selected*/
        i[2]
      );
    },
    d(i) {
      i && o(l);
    }
  };
}
function p(a) {
  let l, e = (
    /*value*/
    a[0] && d(a)
  );
  return {
    c() {
      e && e.c(), l = y();
    },
    m(t, i) {
      e && e.m(t, i), m(t, l, i);
    },
    p(t, [i]) {
      /*value*/
      t[0] ? e ? e.p(t, i) : (e = d(t), e.c(), e.m(l.parentNode, l)) : e && (e.d(1), e = null);
    },
    i: u,
    o: u,
    d(t) {
      t && o(l), e && e.d(t);
    }
  };
}
function q(a, l, e) {
  let { value: t } = l, { type: i } = l, { selected: n = !1 } = l;
  return a.$$set = (s) => {
    "value" in s && e(0, t = s.value), "type" in s && e(1, i = s.type), "selected" in s && e(2, n = s.selected);
  }, [t, i, n];
}
class w extends g {
  constructor(l) {
    super(), b(this, l, q, p, k, { value: 0, type: 1, selected: 2 });
  }
}
export {
  w as default
};
