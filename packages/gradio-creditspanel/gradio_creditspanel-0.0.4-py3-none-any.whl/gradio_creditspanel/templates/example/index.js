const {
  HtmlTagHydration: r,
  SvelteComponent: d,
  attr: u,
  children: o,
  claim_element: h,
  claim_html_tag: m,
  detach: c,
  element: g,
  init: v,
  insert_hydration: y,
  noop: _,
  safe_not_equal: b,
  toggle_class: i
} = window.__gradio__svelte__internal;
function q(n) {
  let e, a;
  return {
    c() {
      e = g("div"), a = new r(!1), this.h();
    },
    l(l) {
      e = h(l, "DIV", { class: !0 });
      var t = o(e);
      a = m(t, !1), t.forEach(c), this.h();
    },
    h() {
      a.a = null, u(e, "class", "prose svelte-180qqaf"), i(
        e,
        "table",
        /*type*/
        n[1] === "table"
      ), i(
        e,
        "gallery",
        /*type*/
        n[1] === "gallery"
      ), i(
        e,
        "selected",
        /*selected*/
        n[2]
      );
    },
    m(l, t) {
      y(l, e, t), a.m(
        /*value*/
        n[0],
        e
      );
    },
    p(l, [t]) {
      t & /*value*/
      1 && a.p(
        /*value*/
        l[0]
      ), t & /*type*/
      2 && i(
        e,
        "table",
        /*type*/
        l[1] === "table"
      ), t & /*type*/
      2 && i(
        e,
        "gallery",
        /*type*/
        l[1] === "gallery"
      ), t & /*selected*/
      4 && i(
        e,
        "selected",
        /*selected*/
        l[2]
      );
    },
    i: _,
    o: _,
    d(l) {
      l && c(e);
    }
  };
}
function w(n, e, a) {
  let { value: l } = e, { type: t } = e, { selected: f = !1 } = e;
  return n.$$set = (s) => {
    "value" in s && a(0, l = s.value), "type" in s && a(1, t = s.type), "selected" in s && a(2, f = s.selected);
  }, [l, t, f];
}
class E extends d {
  constructor(e) {
    super(), v(this, e, w, q, b, { value: 0, type: 1, selected: 2 });
  }
}
export {
  E as default
};
