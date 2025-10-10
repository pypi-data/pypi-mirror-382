(function(global, factory) {
  typeof exports === "object" && typeof module !== "undefined" ? factory(exports, require("vue")) : typeof define === "function" && define.amd ? define(["exports", "vue"], factory) : (global = typeof globalThis !== "undefined" ? globalThis : global || self, factory(global.trame_simput = {}, global.Vue));
})(this, function(exports2, vue) {
  "use strict";
  const FALLBACK_CONVERT = (v) => v;
  const TYPES = {
    uint8: {
      convert(value) {
        const n = Number(value);
        if (Number.isFinite(n)) {
          if (n < 0) {
            return 0;
          }
          if (n > 255) {
            return 255;
          }
          return Math.round(n);
        }
        return null;
      },
      rule(value) {
        const n = Number(value);
        if (!Number.isFinite(n)) {
          return "Provided value is not a valid number";
        }
        if (!Number.isInteger(n)) {
          return "Provided number is not an integer";
        }
        if (n < 0 || n > 255) {
          return "Provided number is outside of the range [0, 255]";
        }
        return true;
      }
    },
    uint16: {
      convert(value) {
        const n = Number(value);
        if (Number.isFinite(n)) {
          if (n < 0) {
            return 0;
          }
          if (n > 65535) {
            return 65535;
          }
          return Math.round(n);
        }
        return null;
      },
      rule(value) {
        const n = Number(value);
        if (!Number.isFinite(n)) {
          return "Provided value is not a valid number";
        }
        if (!Number.isInteger(n)) {
          return "Provided number is not an integer";
        }
        if (n < 0 || n > 65535) {
          return "Provided number is outside of the range [0, 65535]";
        }
        return true;
      }
    },
    uint32: {
      convert(value) {
        const n = Number(value);
        if (Number.isFinite(n)) {
          if (n < 0) {
            return 0;
          }
          if (n > 4294967295) {
            return 4294967295;
          }
          return Math.round(n);
        }
        return null;
      },
      rule(value) {
        const n = Number(value);
        if (!Number.isFinite(n)) {
          return "Provided value is not a valid number";
        }
        if (!Number.isInteger(n)) {
          return "Provided number is not an integer";
        }
        if (n < 0 || n > 4294967295) {
          return "Provided number is outside of the range [0, 4294967295]";
        }
        return true;
      }
    },
    uint64: {
      convert(value) {
        const n = Number(value);
        if (Number.isFinite(n)) {
          if (n < 0) {
            return 0;
          }
          return Math.round(n);
        }
        return null;
      },
      rule(value) {
        const n = Number(value);
        if (!Number.isFinite(n)) {
          return "Provided value is not a valid number";
        }
        if (!Number.isInteger(n)) {
          return "Provided number is not an integer";
        }
        if (n < 0) {
          return "Provided number is outside of the range [0, inf]";
        }
        return true;
      }
    },
    int8: {
      convert(value) {
        const n = Number(value);
        if (Number.isFinite(n)) {
          if (n < -128) {
            return -128;
          }
          if (n > 127) {
            return 127;
          }
          return Math.round(n);
        }
        return null;
      },
      rule(value) {
        const n = Number(value);
        if (!Number.isFinite(n)) {
          return "Provided value is not a valid number";
        }
        if (!Number.isInteger(n)) {
          return "Provided number is not an integer";
        }
        if (n < -128 || n > 127) {
          return "Provided number is outside of the range [-128, 127]";
        }
        return true;
      }
    },
    int16: {
      convert(value) {
        const n = Number(value);
        if (Number.isFinite(n)) {
          if (n < -32768) {
            return -32768;
          }
          if (n > 32767) {
            return 32767;
          }
          return Math.round(n);
        }
        return null;
      },
      rule(value) {
        const n = Number(value);
        if (!Number.isFinite(n)) {
          return "Provided value is not a valid number";
        }
        if (!Number.isInteger(n)) {
          return "Provided number is not an integer";
        }
        if (n < -32768 || n > 32767) {
          return "Provided number is outside of the range [-32768, 32767]";
        }
        return true;
      }
    },
    int32: {
      convert(value) {
        const n = Number(value);
        if (Number.isFinite(n)) {
          if (n < -2147483648) {
            return -2147483648;
          }
          if (n > 2147483647) {
            return 2147483647;
          }
          return Math.round(n);
        }
        return null;
      },
      rule(value) {
        const n = Number(value);
        if (!Number.isFinite(n)) {
          return "Provided value is not a valid number";
        }
        if (!Number.isInteger(n)) {
          return "Provided number is not an integer";
        }
        if (n < -2147483648 || n > 2147483647) {
          return "Provided number is outside of the range [-2147483648, 2147483647]";
        }
        return true;
      }
    },
    int64: {
      convert(value) {
        const n = Number(value);
        if (Number.isFinite(n)) {
          return Math.round(n);
        }
        return null;
      },
      rule(value) {
        const n = Number(value);
        if (!Number.isFinite(n)) {
          return "Provided value is not a valid number";
        }
        if (!Number.isInteger(n)) {
          return "Provided number is not an integer";
        }
        return true;
      }
    },
    float32: {
      convert(value) {
        const n = Number(value);
        if (Number.isNaN(n)) {
          return null;
        }
        return n;
      },
      rule(value) {
        const n = Number(value);
        if (Number.isNaN(n)) {
          return "Provided value is not a number";
        }
        return true;
      }
    },
    float64: {
      convert(value) {
        const n = Number(value);
        if (Number.isNaN(n)) {
          return null;
        }
        return n;
      },
      rule(value) {
        const n = Number(value);
        if (Number.isNaN(n)) {
          return "Provided value is not a number";
        }
        return true;
      }
    },
    string: {
      convert(value) {
        return `${value}`;
      },
      rule() {
        return true;
      }
    },
    bool: {
      convert(value) {
        return !!value;
      },
      rule() {
        return true;
      }
    }
  };
  const MANAGERS = {};
  const { computed: computed$b } = window.Vue;
  function useQuery({ label, name, query, decorator }) {
    const textToQuery = computed$b(() => {
      var _a, _b;
      return `${((_a = name.value) == null ? void 0 : _a.toLowerCase()) || ""} ${((_b = label.value) == null ? void 0 : _b.toLowerCase()) || ""}`;
    });
    const shouldShow = computed$b(() => {
      if (query.value && decorator.value.query) {
        const tokens = query.split(" ");
        if (tokens.length > 1) {
          for (let i = 0; i < tokens.length; i++) {
            const t = tokens[i].trim();
            if (t && textToQuery.value.includes(t)) {
              return true;
            }
          }
          return false;
        }
        return textToQuery.value.includes(this.query);
      }
      return decorator.value.show;
    });
    return {
      textToQuery,
      shouldShow
    };
  }
  function useDecorator({ domains, mtime, name }) {
    const decorator = computed$b(() => {
      var _a, _b;
      mtime.value;
      return ((_b = (_a = domains()[name.value]) == null ? void 0 : _a.decorator) == null ? void 0 : _b.available) || {
        show: true,
        enable: true,
        query: true
      };
    });
    return {
      decorator
    };
  }
  function useConvert({ type }) {
    const convert = computed$b(() => {
      var _a;
      return ((_a = TYPES[type.value]) == null ? void 0 : _a.convert) || FALLBACK_CONVERT;
    });
    return {
      convert
    };
  }
  function useHints({ mtime, domains, name }) {
    const hints = computed$b(() => {
      var _a, _b;
      mtime.value;
      return ((_b = (_a = domains()) == null ? void 0 : _a[name.value]) == null ? void 0 : _b.hints) || [];
    });
    return {
      hints
    };
  }
  function useRule({ type }) {
    const rule = computed$b(() => {
      var _a;
      return ((_a = TYPES[type]) == null ? void 0 : _a.rule) || (() => true);
    });
    return {
      rule
    };
  }
  function debounce(func, wait = 100) {
    let timeout;
    const debounced = (...args) => {
      const context = this;
      const later = () => {
        timeout = null;
        func.apply(context, args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
    debounced.cancel = () => clearTimeout(timeout);
    return debounced;
  }
  class DataManager {
    constructor(namespace, wsClient) {
      this.namespace = namespace;
      this.cache = null;
      this.comm = [];
      this.pendingData = {};
      this.pendingDomain = {};
      this.pendingUI = {};
      this.pendingDirtyData = {};
      this.wsClient = wsClient;
      this.resetCache();
      this.nextTS = 1;
      this.dirtySet = [];
      this.expectedServerProps = {};
      this.subscription = this.wsClient.getConnection().getSession().subscribe("simput.push", ([event]) => {
        const { id, data, domains, type, ui } = event;
        let idChange = false;
        let uiChange = false;
        if (data) {
          delete this.pendingData[id];
          delete this.pendingDirtyData[id];
          const before = JSON.stringify(this.expectedServerProps[id]);
          const after = JSON.stringify(data.properties);
          if (before !== after) {
            idChange = true;
            this.cache.data[id] = data;
            if (before == void 0) {
              this.expectedServerProps[id] = JSON.parse(
                JSON.stringify(data.properties)
              );
            }
          }
          this.cache.data[id].mtime = data.mtime;
          this.cache.data[id].original = JSON.parse(after);
        }
        if (domains) {
          delete this.pendingDomain[id];
          const before = JSON.stringify(this.cache.domains[id]);
          const after = JSON.stringify(domains);
          if (before !== after) {
            idChange = true;
            this.cache.domains[id] = domains;
          }
        }
        if (ui) {
          uiChange = true;
          delete this.pendingUI[type];
          this.cache.ui[type] = ui;
        }
        const notifyPayload = {};
        if (idChange) {
          notifyPayload.id = id;
        }
        if (uiChange) {
          notifyPayload.type = type;
        }
        this.notify("change", notifyPayload);
        if (ui) {
          this.nextTS += 1;
          this.notify("templateTS");
        }
        this.flushDirtySet();
      });
      this.subscriptionUI = this.wsClient.getConnection().getSession().subscribe("simput.event", ([event]) => {
        if (event.topic === "ui-change") {
          const typesToFetch = Object.keys(this.cache.ui);
          this.cache.ui = {};
          for (let i = 0; i < typesToFetch.length; i++) {
            this.getUI(typesToFetch[i]);
          }
        }
        if (event.topic === "data-change") {
          const { ids, action } = event;
          for (let i = 0; i < ids.length; i++) {
            if (this.cache.data[ids[i]]) {
              if (action === "changed") {
                this.getData(ids[i], true);
              }
            }
          }
        }
      });
      this.onDirty = ({ id, name, names }) => {
        if (name) {
          const value = this.cache.data[id].properties[name];
          let idx = this.dirtySet.findIndex(
            (e) => e.id === id && e.name === name
          );
          if (idx > -1)
            this.dirtySet.splice(idx, 1);
          this.dirtySet.push({ id, name, value });
        }
        if (names) {
          for (let i = 0; i < names.length; i++) {
            const name2 = names[i];
            const value = this.cache.data[id].properties[name2];
            let idx = this.dirtySet.findIndex(
              (e) => e.id === id && e.name === name2
            );
            if (idx > -1)
              this.dirtySet.splice(idx, 1);
            this.dirtySet.push({ id, name: name2, value });
          }
        }
        this.flushDirtySet();
      };
    }
    async flushDirtySet() {
      if (!this.dirtySet.length) {
        return;
      }
      if (Object.keys(this.pendingDirtyData).length) {
        return;
      }
      const dirtySet = this.dirtySet;
      this.dirtySet = [];
      dirtySet.forEach(({ id, name, value }) => {
        this.expectedServerProps[id][name] = value;
        this.pendingDirtyData[id] = true;
      });
      await this.wsClient.getRemote().Trame.trigger(`${this.namespace}Update`, [dirtySet]);
      this.flushDirtySet();
    }
    resetCache() {
      this.cache = {
        data: {},
        ui: {},
        domains: {}
      };
      this.wsClient.getRemote().Trame.trigger(`${this.namespace}ResetCache`, []);
    }
    resetDomains() {
      this.cache.domains = {};
    }
    connectBus(bus) {
      if (this.comm.indexOf(bus) === -1) {
        this.comm.push(bus);
        bus.$emit("connect");
        bus.$on("dirty", this.onDirty);
      }
    }
    disconnectBus(bus) {
      const index = this.comm.indexOf(bus);
      if (index > -1) {
        bus.$emit("disconnect");
        bus.$off("dirty", this.onDirty);
        this.comm.splice(index, 1);
      }
    }
    notify(topic, event) {
      for (let i = 0; i < this.comm.length; i++) {
        this.comm[i].$emit(topic, event);
      }
    }
    getData(id, forceFetch = false) {
      const data = this.cache.data[id];
      if ((!data || forceFetch) && !this.pendingData[id]) {
        this.pendingData[id] = true;
        this.wsClient.getRemote().Trame.trigger(`${this.namespace}Fetch`, [], { id });
      }
      return data;
    }
    getDomains(id, forceFetch = false) {
      const domains = this.cache.domains[id];
      if ((!domains || forceFetch) && !this.pendingDomain[id]) {
        this.pendingDomain[id] = true;
        this.wsClient.getRemote().Trame.trigger(`${this.namespace}Fetch`, [], { domains: id });
      }
      return domains;
    }
    getUI(type, forceFetch = false) {
      const ui = this.cache.ui[type];
      if ((!ui || forceFetch) && !this.pendingUI[type]) {
        this.pendingUI[type] = true;
        this.wsClient.getRemote().Trame.trigger(`${this.namespace}Fetch`, [], { type });
      }
      return ui;
    }
    getUITimeStamp() {
      return this.nextTS;
    }
    refresh(id, name) {
      this.wsClient.getRemote().Trame.trigger(`${this.namespace}Refresh`, [id, name]);
    }
  }
  function getSimputManager(id, namespace, client) {
    if (!client) {
      return null;
    }
    if (MANAGERS[id]) {
      return MANAGERS[id];
    }
    const manager = new DataManager(namespace, client);
    MANAGERS[id] = manager;
    return manager;
  }
  function mitt(n) {
    return { all: n = n || /* @__PURE__ */ new Map(), on: function(t, e) {
      var i = n.get(t);
      i ? i.push(e) : n.set(t, [e]);
    }, off: function(t, e) {
      var i = n.get(t);
      i && (e ? i.splice(i.indexOf(e) >>> 0, 1) : n.set(t, []));
    }, emit: function(t, e) {
      var i = n.get(t);
      i && i.slice().map(function(n2) {
        n2(e);
      }), (i = n.get("*")) && i.slice().map(function(n2) {
        n2(t, e);
      });
    } };
  }
  const { ref: ref$8, computed: computed$a, onMounted: onMounted$6, onBeforeUnmount: onBeforeUnmount$5, watch: watch$1, provide: provide$1, inject: inject$a } = window.Vue;
  const emitter = mitt();
  const _sfc_main$b = {
    name: "Simput",
    emits: ["query"],
    props: {
      wsClient: {
        type: Object
      },
      namespace: {
        type: String,
        default: "simput"
      },
      query: {
        type: String,
        default: ""
      }
    },
    setup(props, { emit }) {
      const trame = inject$a("trame");
      const manager = ref$8(null);
      const managerId = ref$8(null);
      const client = computed$a(() => props.wsClient || trame.client);
      const simputChannel = {
        $on: (...args) => emitter.on(...args),
        $once: (...args) => emitter.once(...args),
        $off: (...args) => emitter.off(...args),
        $emit: (...args) => emitter.emit(...args),
        pushQuery: debounce(
          () => {
            var _a;
            return emit("query", ((_a = props.query) == null ? void 0 : _a.toLowerCase()) || "");
          },
          250
        ),
        managerId
      };
      const updateManager = function updateManager2() {
        if (!client.value) {
          return;
        }
        if (manager.value) {
          manager.value.disconnectBus(simputChannel);
        }
        managerId.value = trame.state.get(`${props.namespace}Id`);
        manager.value = getSimputManager(
          managerId.value,
          props.namespace,
          client.value
        );
        manager.value.connectBus(simputChannel);
      };
      onMounted$6(() => {
        updateManager();
      });
      onBeforeUnmount$5(() => {
        if (manager.value) {
          manager.value.disconnectBus(simputChannel);
        }
        manager.value = null;
      });
      watch$1(() => props.namespace, updateManager);
      watch$1(() => props.query, simputChannel.pushQuery);
      const reload = function reload2(name) {
        manager.value.notify("reload", name);
      };
      provide$1("simputChannel", simputChannel);
      provide$1("getSimput", () => manager.value);
      return {
        updateManager,
        reload
      };
    }
  };
  function render$b(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.renderSlot(_ctx.$slots, "default");
  }
  const _export_sfc = (sfc, props) => {
    const target = sfc.__vccOpts || sfc;
    for (const [key, val] of props) {
      target[key] = val;
    }
    return target;
  };
  const Simput = /* @__PURE__ */ _export_sfc(_sfc_main$b, [["render", render$b]]);
  var o = function(t, o2, e) {
    if (!o2.hasOwnProperty(e)) {
      var r = Object.getOwnPropertyDescriptor(t, e);
      Object.defineProperty(o2, e, r);
    }
  };
  const VRuntimeTemplate = { props: { template: String, parent: Object, templateProps: { type: Object, default: function() {
    return {};
  } } }, render: function() {
    if (this.template) {
      var e = this.parent || this.$parent, r = e.$data;
      void 0 === r && (r = {});
      var n = e.$props;
      void 0 === n && (n = {});
      var a = e.$options;
      void 0 === a && (a = {});
      var p = a.components;
      void 0 === p && (p = {});
      var i = a.computed;
      void 0 === i && (i = {});
      var c = a.methods;
      void 0 === c && (c = {});
      var s = this.$data;
      void 0 === s && (s = {});
      var d = this.$props;
      void 0 === d && (d = {});
      var v = this.$options;
      void 0 === v && (v = {});
      var m = v.methods;
      void 0 === m && (m = {});
      var f = v.computed;
      void 0 === f && (f = {});
      var u = v.components;
      void 0 === u && (u = {});
      var h = { $data: {}, $props: {}, $options: {}, components: {}, computed: {}, methods: {} };
      Object.keys(r).forEach(function(t) {
        void 0 === s[t] && (h.$data[t] = r[t]);
      }), Object.keys(n).forEach(function(t) {
        void 0 === d[t] && (h.$props[t] = n[t]);
      }), Object.keys(c).forEach(function(t) {
        void 0 === m[t] && (h.methods[t] = c[t]);
      }), Object.keys(i).forEach(function(t) {
        void 0 === f[t] && (h.computed[t] = i[t]);
      }), Object.keys(p).forEach(function(t) {
        void 0 === u[t] && (h.components[t] = p[t]);
      });
      var $ = Object.keys(h.methods || {}), O = Object.keys(h.$data || {}), b = Object.keys(h.$props || {}), j = Object.keys(this.templateProps), y = O.concat(b).concat($).concat(j), k = (E = e, P = {}, $.forEach(function(t) {
        return o(E, P, t);
      }), P), l = function(t) {
        var e2 = {};
        return t.forEach(function(t2) {
          t2 && Object.getOwnPropertyNames(t2).forEach(function(r2) {
            return o(t2, e2, r2);
          });
        }), e2;
      }([h.$data, h.$props, k, this.templateProps]);
      return vue.h({ template: this.template || "<div></div>", props: y, computed: h.computed, components: h.components, provide: this.$parent.$.provides ? this.$parent.$.provides : {} }, Object.assign({}, l));
    }
    var E, P;
  } };
  const { ref: ref$7, computed: computed$9, onMounted: onMounted$5, onBeforeUnmount: onBeforeUnmount$4, watch, provide, inject: inject$9 } = window.Vue;
  const _sfc_main$a = {
    name: "SimputItem",
    emits: ["dirty"],
    props: {
      itemId: {
        type: String
      },
      noUi: {
        type: Boolean,
        default: false
      }
    },
    components: {
      VRuntimeTemplate
    },
    data() {
      return {
        data: null
      };
    },
    setup(props) {
      const simputChannel = inject$9("simputChannel");
      const getSimput = inject$9("getSimput");
      const data = ref$7(null);
      const ui = ref$7(null);
      const domains = ref$7(null);
      const computedType = computed$9(() => data.value && data.value.type);
      const proxyId = computed$9(() => `${props.itemId}`);
      const update = function update2() {
        if (proxyId.value && getSimput()) {
          data.value = getSimput().getData(proxyId.value);
          domains.value = getSimput().getDomains(proxyId.value);
          if (computedType.value) {
            ui.value = getSimput().getUI(computedType.value);
          }
          simputChannel.pushQuery();
        } else {
          data.value = null;
          ui.value = null;
        }
      };
      const onConnect = function onConnect2() {
        update();
      };
      const onChange = function onChange2({ id, type }) {
        if (id && proxyId.value == id) {
          data.value = getSimput().getData(id);
          domains.value = getSimput().getDomains(id);
        }
        if (type && computedType.value === type) {
          ui.value = getSimput().getUI(computedType.value);
        }
        if (!type && computedType.value && !ui.value) {
          ui.value = getSimput().getUI(computedType.value);
        }
      };
      const onReload = function onReload2(name) {
        if (name === "data") {
          data.value = getSimput().getData(proxyId.value, true);
        }
        if (name === "ui") {
          ui.value = getSimput().getUI(proxyId.value, true);
        }
        if (name === "domain") {
          getSimput().resetDomains();
          domains.value = getSimput().getDomains(proxyId.value, true);
        }
      };
      onMounted$5(() => {
        simputChannel.$on("connect", onConnect);
        simputChannel.$on("change", onChange);
        simputChannel.$on("reload", onReload);
        update();
      });
      onBeforeUnmount$4(() => {
        simputChannel.$off("connect", onConnect);
        simputChannel.$off("change", onChange);
        simputChannel.$off("reload", onReload);
      });
      const available = computed$9(
        () => !!(data.value && domains.value && ui.value)
      );
      const properties = computed$9(() => {
        var _a;
        return (_a = data.value) == null ? void 0 : _a.properties;
      });
      const all = computed$9(() => {
        return {
          id: proxyId.value,
          data: data.value,
          domains: domains.value,
          properties: properties.value
        };
      });
      const dirty = function dirty2(name) {
        var _a;
        simputChannel.$emit("dirty", { id: (_a = data.value) == null ? void 0 : _a.id, name });
      };
      const dirtyMany = function dirtyMany2(names) {
        var _a;
        simputChannel.$emit("dirty", { id: (_a = data.value) == null ? void 0 : _a.id, names });
      };
      watch(
        () => props.itemId,
        () => {
          data.value = null;
          ui.value = null;
          update();
        }
      );
      provide("dirty", (name) => dirty(name));
      provide("dirtyMany", (...names) => dirtyMany(names));
      provide("data", () => data.value);
      provide("domains", () => domains.value);
      provide("properties", () => properties.value);
      provide("uiTS", () => getSimput().getUITimeStamp());
      return {
        available,
        all,
        properties,
        ui,
        data
      };
    }
  };
  const _hoisted_1$3 = { key: 0 };
  function render$a(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_v_runtime_template = vue.resolveComponent("v-runtime-template");
    return _ctx.available ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_1$3, [
      !_ctx.noUi ? (vue.openBlock(), vue.createBlock(_component_v_runtime_template, {
        key: 0,
        template: _ctx.ui,
        data: _ctx.data
      }, null, 8, ["template", "data"])) : vue.createCommentVNode("", true),
      vue.renderSlot(_ctx.$slots, "default", vue.normalizeProps(vue.guardReactiveProps(_ctx.all))),
      vue.renderSlot(_ctx.$slots, "properties", vue.normalizeProps(vue.guardReactiveProps(_ctx.properties)))
    ])) : vue.createCommentVNode("", true);
  }
  const SimputInput = /* @__PURE__ */ _export_sfc(_sfc_main$a, [["render", render$a]]);
  const components = {
    Simput,
    SimputItem: SimputInput
  };
  const { ref: ref$6, computed: computed$8, onMounted: onMounted$4, onBeforeUnmount: onBeforeUnmount$3, inject: inject$8, nextTick, toRef: toRef$5 } = window.Vue;
  function addLabels(values, allTextValues) {
    const result = [];
    const labelMap = {};
    for (let i = 0; i < allTextValues.length; i++) {
      const { text, value } = allTextValues[i];
      labelMap[value] = text;
    }
    for (let i = 0; i < values.length; i++) {
      const value = values[i];
      const text = labelMap[value] || `${value}`;
      result.push({ text, value });
    }
    return result;
  }
  const _sfc_main$9 = {
    name: "swSelect",
    props: {
      name: {
        type: String
      },
      size: {
        type: Number,
        default: 1
      },
      label: {
        type: String
      },
      help: {
        type: String
      },
      mtime: {
        type: Number
      },
      type: {
        type: String
      },
      initial: {},
      // -- add-on --
      items: {
        type: Array
      },
      itemsProperty: {
        type: String
      },
      useRangeHelp: {
        type: Boolean,
        default: false
      },
      rangePrecision: {
        type: Number,
        default: 3
      },
      disabled: {
        type: Boolean,
        default: false
      },
      readonly: {
        type: Boolean,
        default: false
      }
    },
    setup(props) {
      const domains = inject$8("domains");
      const query = ref$6("");
      const { decorator } = useDecorator({
        domains,
        mtime: toRef$5(props.mtime),
        name: toRef$5(props.name)
      });
      const { shouldShow } = useQuery({
        query,
        label: toRef$5(props.label),
        name: toRef$5(props.name),
        decorator
      });
      const { convert } = useConvert({ type: toRef$5(props.type) });
      inject$8("data");
      const properties = inject$8("properties");
      const dirty = inject$8("dirty");
      const uiTS = inject$8("uiTS");
      const simputChannel = inject$8("simputChannel");
      ref$6(false);
      const tsKey = ref$6("__default__");
      const onQuery = function onQuery2(query2) {
        query2.value = query2;
      };
      const onUpdateUI = function onUpdateUI2() {
        const newValue = `__${props.name}__${uiTS()}`;
        if (tsKey.value !== newValue) {
          nextTick(() => {
            tsKey.value = newValue;
          });
        }
      };
      onMounted$4(() => {
        simputChannel.$on("query", onQuery);
        simputChannel.$on("templateTS", onUpdateUI);
        onUpdateUI();
      });
      onBeforeUnmount$3(() => {
        simputChannel.$off("query", onQuery);
        simputChannel.$off("templateTS", onUpdateUI);
      });
      const model = computed$8({
        get() {
          props.mtime;
          return properties() && properties()[props.name];
        },
        set(v) {
          properties()[props.name] = v;
        }
      });
      const multiple = computed$8(() => {
        return Number(props.size) === -1;
      });
      const validate = function validate2() {
        if (multiple.value || Array.isArray(model.value)) {
          model.value = model.value.map((v) => convert.value(v));
        } else {
          model.value = convert.value(model.value);
        }
        dirty(props.name);
      };
      const computedItems = computed$8(() => {
        var _a, _b, _c, _d, _e, _f;
        if (props.items) {
          return props.items;
        }
        if (props.itemsProperty) {
          const available = ((_b = (_a = domains()[props.itemsProperty]) == null ? void 0 : _a.LabelList) == null ? void 0 : _b.available) || [];
          const filteredValues = properties()[props.itemsProperty];
          return addLabels(filteredValues, available);
        }
        const availableOptions = domains()[props.name] || {};
        return ((_c = availableOptions == null ? void 0 : availableOptions.List) == null ? void 0 : _c.available) || ((_d = availableOptions == null ? void 0 : availableOptions.HasTags) == null ? void 0 : _d.available) || ((_e = availableOptions == null ? void 0 : availableOptions.ProxyBuilder) == null ? void 0 : _e.available) || ((_f = availableOptions == null ? void 0 : availableOptions.FieldSelector) == null ? void 0 : _f.available);
      });
      computed$8(() => {
        var _a, _b, _c;
        return `${((_a = props.name) == null ? void 0 : _a.toLowerCase()) || ""} ${((_b = props.label) == null ? void 0 : _b.toLowerCase()) || ""} ${((_c = props.help) == null ? void 0 : _c.toLowerCase()) || ""} ${JSON.stringify(
          computedItems.value
        )}`;
      });
      const selectedItem = computed$8(() => {
        props.mtime;
        return computedItems.find(({ value }) => value === model.value);
      });
      const computedHelp = computed$8(() => {
        var _a;
        if (!props.useRangeHelp) {
          return props.help;
        }
        if (selectedItem.value && ((_a = selectedItem.value) == null ? void 0 : _a.range)) {
          const rangeStr = selectedItem.value.range.map((v) => v.toFixed(props.rangePrecision)).join(", ");
          if (props.help) {
            return `${props.help} - [${rangeStr}]`;
          }
          return `[${rangeStr}]`;
        }
        return props.help;
      });
      return {
        tsKey,
        computedHelp,
        model,
        computedItems,
        multiple,
        validate,
        decorator,
        shouldShow
      };
    },
    methods: {
      resolveItemTitle(item) {
        return item.title ?? item.text ?? void 0;
      }
    }
  };
  function render$9(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_v_list_subheader = vue.resolveComponent("v-list-subheader");
    const _component_v_list_item = vue.resolveComponent("v-list-item");
    const _component_v_select = vue.resolveComponent("v-select");
    const _component_v_col = vue.resolveComponent("v-col");
    return vue.withDirectives((vue.openBlock(), vue.createBlock(_component_v_col, { class: "py-0" }, {
      default: vue.withCtx(() => [
        (vue.openBlock(), vue.createBlock(_component_v_select, {
          key: _ctx.tsKey,
          label: _ctx.label,
          modelValue: _ctx.model,
          "onUpdate:modelValue": [
            _cache[0] || (_cache[0] = ($event) => _ctx.model = $event),
            _ctx.validate
          ],
          variant: "underlined",
          items: _ctx.computedItems,
          "item-title": _ctx.resolveItemTitle,
          "item-value": "value",
          multiple: _ctx.multiple,
          hint: _ctx.computedHelp,
          "persistent-hint": !!(_ctx.useRangeHelp || _ctx.help),
          disabled: _ctx.disabled || !_ctx.decorator.enable,
          readonly: _ctx.readonly
        }, {
          item: vue.withCtx(({ item, props }) => [
            item.raw.header ? (vue.openBlock(), vue.createBlock(_component_v_list_subheader, { key: 0 }, {
              default: vue.withCtx(() => [
                vue.createTextVNode(vue.toDisplayString(item.raw.header), 1)
              ]),
              _: 2
            }, 1024)) : (vue.openBlock(), vue.createBlock(_component_v_list_item, vue.normalizeProps(vue.mergeProps({ key: 1 }, props)), null, 16))
          ]),
          _: 1
        }, 8, ["label", "modelValue", "items", "item-title", "multiple", "onUpdate:modelValue", "hint", "persistent-hint", "disabled", "readonly"]))
      ]),
      _: 1
    }, 512)), [
      [vue.vShow, _ctx.shouldShow]
    ]);
  }
  const SwSelect = /* @__PURE__ */ _export_sfc(_sfc_main$9, [["render", render$9]]);
  const { ref: ref$5, computed: computed$7, onMounted: onMounted$3, onBeforeUnmount: onBeforeUnmount$2, inject: inject$7, toRef: toRef$4 } = window.Vue;
  const _sfc_main$8 = {
    name: "swSlider",
    props: {
      name: {
        type: String
      },
      size: {
        type: Number,
        default: 1
      },
      label: {
        type: String
      },
      help: {
        type: String
      },
      mtime: {
        type: Number
      },
      type: {
        type: String
      },
      initial: {},
      // --- custom to current widget ---
      layout: {
        type: String
      },
      sizeControl: {
        type: Boolean,
        default: false
      },
      min: {
        type: Number
      },
      max: {
        type: Number
      },
      step: {
        type: Number
      },
      disabled: {
        type: Boolean,
        default: false
      },
      readonly: {
        type: Boolean,
        default: false
      }
    },
    setup(props) {
      const simputChannel = inject$7("simputChannel");
      const data = inject$7("data");
      const properties = inject$7("properties");
      const domains = inject$7("domains");
      const dirty = inject$7("dirty");
      const showHelp = ref$5(false);
      const dynamicSize = ref$5(props.size);
      const query = ref$5("");
      const { decorator } = useDecorator({
        domains,
        mtime: toRef$4(props.mtime),
        name: toRef$4(props.name)
      });
      const { shouldShow, textToQuery } = useQuery({
        query,
        label: toRef$4(props.label),
        name: toRef$4(props.name),
        decorator
      });
      const { convert } = useConvert({ type: toRef$4(props.type) });
      const { rule } = useRule({ type: toRef$4(props.type) });
      const { hints } = useHints({
        domains,
        mtime: toRef$4(props.mtime),
        name: toRef$4(props.name)
      });
      const onQuery = function onQuery2(query2) {
        query2.value = query2;
      };
      onMounted$3(() => {
        simputChannel.$on("query", onQuery);
      });
      onBeforeUnmount$2(() => {
        simputChannel.$off("query", onQuery);
      });
      const model = computed$7({
        get() {
          props.mtime;
          dynamicSize.value;
          return properties() && properties()[props.name];
        },
        set(v) {
          properties()[props.name] = v;
        }
      });
      const computedLayout = computed$7(() => {
        var _a, _b;
        props.mtime;
        return props.layout || ((_b = (_a = domains()[props.name]) == null ? void 0 : _a.UI) == null ? void 0 : _b.layout) || "vertical";
      });
      const computedSize = computed$7(() => {
        if (Number(props.size) !== 1) {
          return Math.max(props.size, model.value.length);
        }
        return Number(props.size);
      });
      const computedSizeControl = computed$7(() => {
        var _a, _b;
        props.mtime;
        return props.sizeControl || ((_b = (_a = domains()[props.name]) == null ? void 0 : _a.UI) == null ? void 0 : _b.sizeControl);
      });
      const computedMin = computed$7(() => {
        var _a, _b, _c, _d, _e, _f;
        if (props.min != null) {
          return props.min;
        }
        const dataRange = ((_c = (_b = (_a = domains()) == null ? void 0 : _a[props.name]) == null ? void 0 : _b.Range) == null ? void 0 : _c.available) || ((_f = (_e = (_d = domains()) == null ? void 0 : _d[props.name]) == null ? void 0 : _e.range) == null ? void 0 : _f.available);
        if (dataRange) {
          return dataRange[0];
        }
        return 0;
      });
      const computedMax = computed$7(() => {
        var _a, _b, _c, _d, _e, _f;
        if (props.max != null) {
          return props.max;
        }
        const dataRange = ((_c = (_b = (_a = domains()) == null ? void 0 : _a[props.name]) == null ? void 0 : _b.Range) == null ? void 0 : _c.available) || ((_f = (_e = (_d = domains()) == null ? void 0 : _d[props.name]) == null ? void 0 : _e.range) == null ? void 0 : _f.available);
        if (dataRange) {
          return dataRange[1];
        }
        return 100;
      });
      const computedStep = computed$7(() => {
        if (props.step) {
          return props.step;
        }
        if (props.type.includes("int")) {
          return 1;
        }
        return 0.01;
      });
      const levelToType = function levelToType2(level) {
        switch (level) {
          case 0:
            return "info";
          case 1:
            return "warning";
          case 2:
            return "error";
          default:
            return "success";
        }
      };
      const levelToIcon = function levelToIcon2(level) {
        switch (level) {
          case 0:
            return "mdi-information-outline";
          case 1:
            return "mdi-alert-octagon-outline";
          case 2:
            return "mdi-alert-outline";
          default:
            return "mdi-brain";
        }
      };
      const validate = function validate2(component = 0) {
        const value = component ? model.value[component - 1] : model.value;
        if (Number(props.size) !== 1) {
          model.value[component - 1] = convert.value(value);
          if (model.value[component - 1] === null) {
            model.value[component - 1] = props.initial[component - 1];
          }
          model.value = model.value.slice();
        } else {
          model.value !== convert.value(value);
          model.value = convert.value(value);
          if (model.value === null) {
            model.value = props.initial;
          }
        }
        dirty(props.name);
      };
      const addEntry = function addEntry2() {
        dynamicSize.value = model.value.length + 1;
        model.value.length = dynamicSize.value;
        validate(dynamicSize.value);
      };
      const deleteEntry = function deleteEntry2(index) {
        model.value.splice(index, 1);
        dirty(props.name);
      };
      const getComponentProps = function getComponentProps2(index) {
        if (computedLayout.value === "vertical") {
          return { cols: 12 };
        }
        if (computedLayout.value === "l2") {
          return { cols: 6 };
        }
        if (computedLayout.value === "l3") {
          return { cols: 4 };
        }
        if (computedLayout.value === "l4") {
          return { cols: 3 };
        }
        if (computedLayout.value === "m3-half") {
          const attrs = { cols: 4 };
          if (index === 3) {
            attrs.offset = 4;
          }
          if (index === 5) {
            attrs.offset = 8;
          }
          return attrs;
        }
        return {};
      };
      return {
        getComponentProps,
        validate,
        addEntry,
        deleteEntry,
        levelToIcon,
        levelToType,
        computedMin,
        computedMax,
        computedStep,
        computedSize,
        computedSizeControl,
        showHelp,
        data,
        decorator,
        rule,
        hints,
        shouldShow,
        model
      };
    }
  };
  const _hoisted_1$2 = { style: { "position": "absolute", "right": "10px", "top": "-1px", "z-index": "1" } };
  const _hoisted_2$1 = { class: "text-caption text--secondary" };
  const _hoisted_3$1 = {
    key: 0,
    class: "text-caption text--secondary"
  };
  const _hoisted_4 = {
    key: 0,
    class: "mt-0 mb-2 text-caption text--secondary"
  };
  const _hoisted_5 = {
    class: "text-truncate text-right text-caption text--secondary",
    style: { "max-width": "60px", "min-width": "60px" }
  };
  function render$8(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_v_btn = vue.resolveComponent("v-btn");
    const _component_v_divider = vue.resolveComponent("v-divider");
    const _component_v_col = vue.resolveComponent("v-col");
    const _component_v_row = vue.resolveComponent("v-row");
    const _component_v_slider = vue.resolveComponent("v-slider");
    const _component_v_alert = vue.resolveComponent("v-alert");
    const _component_v_container = vue.resolveComponent("v-container");
    return vue.withDirectives((vue.openBlock(), vue.createBlock(_component_v_container, {
      fluid: "",
      style: { "position": "relative" }
    }, {
      default: vue.withCtx(() => [
        vue.createElementVNode("div", _hoisted_1$2, [
          _ctx.help && _ctx.size > 1 ? (vue.openBlock(), vue.createBlock(_component_v_btn, {
            key: 0,
            class: "elevation-0",
            icon: "mdi-lifebuoy",
            size: "x-small",
            onClick: _cache[0] || (_cache[0] = ($event) => _ctx.showHelp = !_ctx.showHelp)
          })) : vue.createCommentVNode("", true),
          _ctx.computedSizeControl ? (vue.openBlock(), vue.createBlock(_component_v_btn, {
            key: 1,
            class: "elevation-0",
            icon: "mdi-plus-circle-outline",
            size: "x-small",
            onClick: _ctx.addEntry
          }, null, 8, ["onClick"])) : vue.createCommentVNode("", true)
        ]),
        vue.createVNode(_component_v_row, null, {
          default: vue.withCtx(() => [
            _ctx.label && _ctx.size != 1 ? (vue.openBlock(), vue.createBlock(_component_v_col, {
              key: 0,
              class: "py-0"
            }, {
              default: vue.withCtx(() => [
                vue.createElementVNode("div", _hoisted_2$1, vue.toDisplayString(_ctx.label), 1),
                vue.createVNode(_component_v_divider),
                _ctx.help && _ctx.showHelp ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_3$1, vue.toDisplayString(_ctx.help), 1)) : vue.createCommentVNode("", true)
              ]),
              _: 1
            })) : vue.createCommentVNode("", true)
          ]),
          _: 1
        }),
        _ctx.model != null ? (vue.openBlock(), vue.createBlock(_component_v_row, { key: 0 }, {
          default: vue.withCtx(() => [
            _ctx.size == 1 ? (vue.openBlock(), vue.createBlock(_component_v_col, {
              key: 0,
              class: "pt-0 pb-1"
            }, {
              default: vue.withCtx(() => [
                vue.createVNode(_component_v_row, {
                  "no-gutters": "",
                  class: "align-center"
                }, {
                  default: vue.withCtx(() => [
                    vue.createVNode(_component_v_col, {
                      cols: "9",
                      class: "text-truncate text--secondary"
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode(vue.toDisplayString(_ctx.label), 1)
                      ]),
                      _: 1
                    }),
                    vue.createVNode(_component_v_col, { class: "text-truncate text-right text-caption text--secondary" }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode(vue.toDisplayString(_ctx.model), 1)
                      ]),
                      _: 1
                    }),
                    _ctx.help ? (vue.openBlock(), vue.createBlock(_component_v_btn, {
                      key: 0,
                      class: "elevation-0",
                      icon: "mdi-lifebuoy",
                      size: "x-small",
                      onClick: _cache[1] || (_cache[1] = ($event) => _ctx.showHelp = !_ctx.showHelp)
                    })) : vue.createCommentVNode("", true)
                  ]),
                  _: 1
                }),
                vue.createVNode(_component_v_slider, {
                  name: `${_ctx.data().type}:${_ctx.name}:${_ctx.i}`,
                  modelValue: _ctx.model,
                  "onUpdate:modelValue": [
                    _cache[2] || (_cache[2] = ($event) => _ctx.model = $event),
                    _cache[3] || (_cache[3] = ($event) => _ctx.validate())
                  ],
                  "hide-details": "",
                  rules: [_ctx.rule],
                  min: _ctx.computedMin,
                  max: _ctx.computedMax,
                  step: _ctx.computedStep,
                  disabled: _ctx.disabled || !_ctx.decorator.enable,
                  readonly: _ctx.readonly
                }, null, 8, ["name", "modelValue", "rules", "min", "max", "step", "disabled", "readonly"]),
                _ctx.help && _ctx.showHelp ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_4, vue.toDisplayString(_ctx.help), 1)) : vue.createCommentVNode("", true),
                (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(_ctx.hints, (hint, idx) => {
                  return vue.openBlock(), vue.createBlock(_component_v_alert, {
                    key: idx,
                    class: "mb-1",
                    type: _ctx.levelToType(hint.level),
                    text: hint.message
                  }, null, 8, ["type", "text"]);
                }), 128))
              ]),
              _: 1
            })) : vue.createCommentVNode("", true),
            _ctx.size != 1 ? (vue.openBlock(true), vue.createElementBlock(vue.Fragment, { key: 1 }, vue.renderList(_ctx.computedSize, (i) => {
              return vue.openBlock(), vue.createBlock(_component_v_col, vue.mergeProps({
                class: "py-1",
                key: i,
                ref_for: true
              }, _ctx.getComponentProps(i - 1)), {
                default: vue.withCtx(() => [
                  vue.createVNode(_component_v_row, {
                    "no-gutters": "",
                    class: "align-center"
                  }, {
                    default: vue.withCtx(() => [
                      vue.createVNode(_component_v_slider, {
                        class: "mt-0",
                        name: `${_ctx.data().type}:${_ctx.name}:${i}`,
                        modelValue: _ctx.model[i - 1],
                        "onUpdate:modelValue": [($event) => _ctx.model[i - 1] = $event, ($event) => _ctx.validate(i)],
                        "hide-details": "",
                        rules: [_ctx.rule],
                        min: _ctx.computedMin,
                        max: _ctx.computedMax,
                        step: _ctx.computedStep,
                        disabled: _ctx.disabled || !_ctx.decorator.enable,
                        readonly: _ctx.readonly
                      }, null, 8, ["name", "modelValue", "onUpdate:modelValue", "rules", "min", "max", "step", "disabled", "readonly"]),
                      vue.createElementVNode("div", _hoisted_5, vue.toDisplayString(_ctx.model[i - 1]), 1),
                      _ctx.computedSizeControl ? (vue.openBlock(), vue.createBlock(_component_v_btn, {
                        key: 0,
                        class: "ml-2 elevation-0",
                        icon: "mdi-minus-circle-outline",
                        size: "x-small",
                        onClick: ($event) => _ctx.deleteEntry(i - 1),
                        disabled: !_ctx.decorator.enable
                      }, null, 8, ["onClick", "disabled"])) : vue.createCommentVNode("", true)
                    ]),
                    _: 2
                  }, 1024),
                  (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(_ctx.hints, (hint, idx) => {
                    return vue.openBlock(), vue.createBlock(_component_v_alert, {
                      key: idx,
                      class: "mb-1",
                      type: _ctx.levelToType(hint.level),
                      text: hint.message
                    }, null, 8, ["type", "text"]);
                  }), 128))
                ]),
                _: 2
              }, 1040);
            }), 128)) : vue.createCommentVNode("", true)
          ]),
          _: 1
        })) : vue.createCommentVNode("", true)
      ]),
      _: 1
    }, 512)), [
      [vue.vShow, _ctx.shouldShow]
    ]);
  }
  const SwSlider = /* @__PURE__ */ _export_sfc(_sfc_main$8, [["render", render$8]]);
  const { ref: ref$4, computed: computed$6, onMounted: onMounted$2, onBeforeUnmount: onBeforeUnmount$1, inject: inject$6, toRef: toRef$3 } = window.Vue;
  const _sfc_main$7 = {
    name: "swSwitch",
    props: {
      name: {
        type: String
      },
      size: {
        type: Number,
        default: 1
      },
      label: {
        type: String
      },
      help: {
        type: String
      },
      mtime: {
        type: Number
      },
      type: {
        type: String
      },
      initial: {},
      disabled: {
        type: Boolean,
        default: false
      },
      readonly: {
        type: Boolean,
        default: false
      }
    },
    setup(props) {
      const showHelp = ref$4(false);
      const query = ref$4("");
      const domains = inject$6("domains");
      const simputChannel = inject$6("simputChannel");
      const properties = inject$6("properties");
      const dirty = inject$6("dirty");
      const { decorator } = useDecorator({
        domains,
        mtime: toRef$3(props.mtime),
        name: toRef$3(props.name)
      });
      const { shouldShow, textToQuery } = useQuery({
        query,
        label: toRef$3(props.label),
        name: toRef$3(props.name),
        decorator
      });
      const { convert } = useConvert({ type: toRef$3(props.type) });
      const onQuery = function onQuery2(query2) {
        query2.value = query2;
      };
      onMounted$2(() => {
        simputChannel.$on("query", onQuery);
      });
      onBeforeUnmount$1(() => {
        simputChannel.$off("query", onQuery);
      });
      const model = computed$6({
        get() {
          props.mtime;
          return properties() && properties()[props.name];
        },
        set(v) {
          properties()[props.name] = v;
        }
      });
      const validate = function validate2() {
        model.value = convert.value(model.value);
        dirty(props.name);
      };
      return {
        validate,
        showHelp,
        decorator,
        model,
        shouldShow
      };
    }
  };
  function render$7(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_v_switch = vue.resolveComponent("v-switch");
    const _component_v_spacer = vue.resolveComponent("v-spacer");
    const _component_v_btn = vue.resolveComponent("v-btn");
    const _component_v_row = vue.resolveComponent("v-row");
    const _component_v_col = vue.resolveComponent("v-col");
    return vue.withDirectives((vue.openBlock(), vue.createBlock(_component_v_col, null, {
      default: vue.withCtx(() => [
        vue.createVNode(_component_v_row, {
          class: "ma-0 align-center",
          style: { "position": "relative" }
        }, {
          default: vue.withCtx(() => [
            vue.createVNode(_component_v_switch, {
              class: "py-0 mt-0",
              label: _ctx.label,
              hint: _ctx.help,
              modelValue: _ctx.model,
              "onUpdate:modelValue": [
                _cache[0] || (_cache[0] = ($event) => _ctx.model = $event),
                _ctx.validate
              ],
              "hide-details": "",
              disabled: _ctx.disabled || !_ctx.decorator.enable,
              readonly: _ctx.readonly
            }, null, 8, ["label", "hint", "modelValue", "onUpdate:modelValue", "disabled", "readonly"]),
            vue.createVNode(_component_v_spacer),
            _ctx.help ? (vue.openBlock(), vue.createBlock(_component_v_btn, {
              key: 0,
              class: "elevation-0",
              icon: "mdi-lifebuoy",
              size: "x-small",
              style: { "position": "absolute", "right": "0" },
              onClick: _cache[1] || (_cache[1] = ($event) => _ctx.showHelp = !_ctx.showHelp)
            })) : vue.createCommentVNode("", true)
          ]),
          _: 1
        }),
        _ctx.help && _ctx.showHelp ? (vue.openBlock(), vue.createBlock(_component_v_row, {
          key: 0,
          class: "ma-0 text-caption text--secondary"
        }, {
          default: vue.withCtx(() => [
            vue.createTextVNode(vue.toDisplayString(_ctx.help), 1)
          ]),
          _: 1
        })) : vue.createCommentVNode("", true)
      ]),
      _: 1
    }, 512)), [
      [vue.vShow, _ctx.shouldShow]
    ]);
  }
  const SwSwitch = /* @__PURE__ */ _export_sfc(_sfc_main$7, [["render", render$7]]);
  const { ref: ref$3, computed: computed$5, inject: inject$5 } = window.Vue;
  const _sfc_main$6 = {
    name: "swTextArea",
    props: {
      name: {
        type: String
      },
      size: {
        type: Number,
        default: 1
      },
      label: {
        type: String
      },
      help: {
        type: String
      },
      mtime: {
        type: Number
      },
      // --- text-area-props ---
      "auto-grow": {
        type: Boolean,
        default: false
      },
      autofocus: {
        type: Boolean,
        default: false
      },
      clearable: {
        type: Boolean,
        default: false
      },
      disabled: {
        type: Boolean,
        default: false
      },
      readonly: {
        type: Boolean,
        default: false
      },
      "no-resize": {
        type: Boolean,
        default: false
      },
      rows: {
        type: [String, Number],
        default: 5
      }
    },
    setup(props) {
      ref$3(false);
      const properties = inject$5("properties");
      const domains = inject$5("domains");
      const dirty = inject$5("dirty");
      const model = computed$5({
        get() {
          props.mtime;
          return properties() && properties()[props.name] || "";
        },
        set(v) {
          properties()[props.name] = v;
        }
      });
      const decorator = computed$5(() => {
        var _a, _b;
        props.mtime;
        return ((_b = (_a = domains()[props.name]) == null ? void 0 : _a.decorator) == null ? void 0 : _b.available) || {
          show: true,
          enable: true
        };
      });
      const validate = function validate2() {
        dirty(props.name);
      };
      return {
        validate,
        decorator,
        model
      };
    }
  };
  function render$6(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_v_textarea = vue.resolveComponent("v-textarea");
    return vue.withDirectives((vue.openBlock(), vue.createBlock(_component_v_textarea, {
      density: "compact",
      label: _ctx.label,
      hint: _ctx.help,
      modelValue: _ctx.model,
      "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => _ctx.model = $event),
      onChange: _ctx.validate,
      "auto-grow": _ctx.auto - _ctx.grow,
      autofocus: _ctx.autofocus,
      clearable: _ctx.clearable,
      readonly: _ctx.readonly,
      "no-resize": _ctx.no - _ctx.resize,
      rows: _ctx.rows,
      disabled: _ctx.disabled || !_ctx.decorator.enable
    }, null, 8, ["label", "hint", "modelValue", "onChange", "auto-grow", "autofocus", "clearable", "readonly", "no-resize", "rows", "disabled"])), [
      [vue.vShow, _ctx.decorator.show]
    ]);
  }
  const SwTextArea = /* @__PURE__ */ _export_sfc(_sfc_main$6, [["render", render$6]]);
  const { ref: ref$2, computed: computed$4, onMounted: onMounted$1, onBeforeUnmount, inject: inject$4, toRef: toRef$2 } = window.Vue;
  const _sfc_main$5 = {
    name: "swTextField",
    props: {
      name: {
        type: String
      },
      size: {
        type: Number,
        default: 1
      },
      label: {
        type: String
      },
      help: {
        type: String
      },
      mtime: {
        type: Number
      },
      type: {
        type: String
      },
      initial: {},
      // --- custom to current widget ---
      editColor: {
        type: String,
        default: "transparent"
      },
      layout: {
        type: String
      },
      sizeControl: {
        type: Boolean,
        default: false
      },
      allowRefresh: {
        type: Boolean,
        default: false
      },
      newValue: {
        type: String,
        default: "same"
      },
      disabled: {
        type: Boolean,
        default: false
      },
      readonly: {
        type: Boolean,
        default: false
      },
      proxyType: {
        type: String
      }
    },
    setup(props) {
      const domains = inject$4("domains");
      const showHelp = ref$2(false);
      const dynamicSize = ref$2(props.size.value);
      const query = ref$2("");
      const { decorator } = useDecorator({
        domains,
        mtime: toRef$2(props.mtime),
        name: toRef$2(props.name)
      });
      const { shouldShow, textToQuery } = useQuery({
        query,
        label: toRef$2(props.label),
        name: toRef$2(props.name),
        decorator
      });
      const { convert } = useConvert({ type: toRef$2(props.type) });
      const { rule } = useRule({ type: toRef$2(props.type) });
      const { hints } = useHints({
        domains,
        mtime: toRef$2(props.mtime),
        name: toRef$2(props.name)
      });
      const simputChannel = inject$4("simputChannel");
      const properties = inject$4("properties");
      const data = inject$4("data");
      const getSimput = inject$4("getSimput");
      const dirty = inject$4("dirty");
      const onQuery = function onQuery2(query2) {
        query2.value = query2;
      };
      onMounted$1(() => {
        simputChannel.$on("query", onQuery);
      });
      onBeforeUnmount(() => {
        simputChannel.$off("query", onQuery);
      });
      const model = computed$4({
        get() {
          props.mtime;
          dynamicSize.value;
          const value = properties() && properties()[props.name];
          if (!value && props.size > 1) {
            const emptyArray = [];
            emptyArray.length = props.size;
            return emptyArray;
          }
          return value;
        },
        set(v) {
          properties()[props.name] = v;
        }
      });
      const computedLayout = computed$4(() => {
        var _a, _b;
        props.mtime;
        return props.layout || ((_b = (_a = domains()[props.name]) == null ? void 0 : _a.UI) == null ? void 0 : _b.layout) || "horizontal";
      });
      const computedSize = computed$4(() => {
        var _a;
        if (Number(props.size) !== 1) {
          return Math.max(props.size || 1, ((_a = model.value) == null ? void 0 : _a.length) || 0);
        }
        return Number(props.size);
      });
      const computedSizeControl = computed$4(() => {
        var _a, _b;
        props.mtime;
        return props.sizeControl || ((_b = (_a = domains()[props.name]) == null ? void 0 : _a.UI) == null ? void 0 : _b.sizeControl);
      });
      const levelToType = function levelToType2(level) {
        switch (level) {
          case 0:
            return "info";
          case 1:
            return "warning";
          case 2:
            return "error";
          default:
            return "success";
        }
      };
      const levelToIcon = function levelToIcon2(level) {
        switch (level) {
          case 0:
            return "mdi-information-outline";
          case 1:
            return "mdi-alert-octagon-outline";
          case 2:
            return "mdi-alert-outline";
          default:
            return "mdi-brain";
        }
      };
      const validate = function validate2(component = 0) {
        var _a;
        const value = component ? model.value[component - 1] : model.value;
        const newValue = convert.value(value);
        if (Number(props.size) !== 1) {
          model.value[component - 1] = newValue;
          if (newValue === null) {
            model.value[component - 1] = (_a = props.initial) == null ? void 0 : _a[component - 1];
          }
          model.value = model.value.slice();
        } else {
          model.value = newValue;
          if (model.value === null) {
            model.value = props.initial;
          }
        }
        dirty(props.name);
      };
      const refresh = function refresh2() {
        getSimput().refresh(data().id, props.name);
      };
      const addEntry = function addEntry2() {
        if (!model.value) {
          model.value = [];
        }
        if (props.type == "proxy") {
          getSimput().wsClient.getConnection().getSession().call("simput.create_proxy", [
            simputChannel.managerId.value,
            props.proxyType
          ]).then((proxy_id) => {
            if (proxy_id != void 0) {
              model.value.push(proxy_id);
              dirty(props.name);
            }
            dynamicSize.value = model.value.length;
            validate(dynamicSize.value);
          });
        } else {
          if (props.newValue === "null") {
            model.value.push(null);
          } else if (props.newValue === "same") {
            model.value.push(model.value[model.value.length - 2]);
          }
          dynamicSize.value = model.value.length;
          validate(dynamicSize.value);
        }
      };
      const deleteEntry = function deletEntry(index) {
        model.value.splice(index, 1);
        dirty(props.name);
      };
      const getComponentProps = function getComponentProps2(index) {
        if (computedLayout.value === "vertical") {
          return { cols: 12 };
        }
        if (computedLayout.value === "l2") {
          return { cols: 6 };
        }
        if (computedLayout.value === "l3") {
          return { cols: 4 };
        }
        if (computedLayout.value === "l4") {
          return { cols: 3 };
        }
        if (computedLayout.value === "m3-half") {
          const attrs = { cols: 4 };
          if (index === 3) {
            attrs.offset = 4;
          }
          if (index === 5) {
            attrs.offset = 8;
          }
          return attrs;
        }
        return {};
      };
      const color = function color2(component = 0) {
        var _a, _b;
        if (component && ((_a = model.value) == null ? void 0 : _a[component - 1]) !== ((_b = props.initial) == null ? void 0 : _b[component - 1])) {
          return props.editColor;
        }
        if (!component && model.value !== props.initial) {
          return props.editColor;
        }
        return void 0;
      };
      const update = function update2(component = 0) {
        const value = component ? model.value[component - 1] : model.value;
        if (rule.value(value) === true) {
          if (Number(props.size) !== 1) {
            model.value[component - 1] = convert.value(value);
          } else {
            model.value = convert.value(value);
          }
          dirty(props.name);
        }
      };
      return {
        showHelp,
        computedSize,
        getComponentProps,
        validate,
        update,
        data,
        color,
        levelToType,
        levelToIcon,
        computedSizeControl,
        addEntry,
        deleteEntry,
        hints,
        rule,
        refresh,
        shouldShow,
        decorator,
        model
      };
    }
  };
  const _hoisted_1$1 = { style: { "position": "absolute", "right": "10px", "top": "-1px", "z-index": "1" } };
  const _hoisted_2 = { class: "text-caption text--secondary" };
  const _hoisted_3 = {
    key: 0,
    class: "text-caption text--secondary"
  };
  function render$5(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_v_btn = vue.resolveComponent("v-btn");
    const _component_v_divider = vue.resolveComponent("v-divider");
    const _component_v_col = vue.resolveComponent("v-col");
    const _component_v_row = vue.resolveComponent("v-row");
    const _component_v_text_field = vue.resolveComponent("v-text-field");
    const _component_v_alert = vue.resolveComponent("v-alert");
    return vue.withDirectives((vue.openBlock(), vue.createBlock(_component_v_col, {
      fluid: "",
      style: { "position": "relative" },
      class: "py-5"
    }, {
      default: vue.withCtx(() => [
        vue.createElementVNode("div", _hoisted_1$1, [
          _ctx.allowRefresh ? (vue.openBlock(), vue.createBlock(_component_v_btn, {
            key: 0,
            class: "elevation-0",
            icon: "mdi-sync",
            size: "x-small",
            onClick: _ctx.refresh
          }, null, 8, ["onClick"])) : vue.createCommentVNode("", true),
          _ctx.help ? (vue.openBlock(), vue.createBlock(_component_v_btn, {
            key: 1,
            class: "elevation-0",
            icon: "mdi-lifebuoy",
            size: "x-small",
            onClick: _cache[0] || (_cache[0] = ($event) => _ctx.showHelp = !_ctx.showHelp)
          })) : vue.createCommentVNode("", true),
          _ctx.computedSizeControl ? (vue.openBlock(), vue.createBlock(_component_v_btn, {
            key: 2,
            class: "elevation-0",
            icon: "mdi-plus-circle-outline",
            size: "x-small",
            onClick: _ctx.addEntry
          }, null, 8, ["onClick"])) : vue.createCommentVNode("", true)
        ]),
        vue.createVNode(_component_v_row, null, {
          default: vue.withCtx(() => [
            _ctx.label && _ctx.size != 1 ? (vue.openBlock(), vue.createBlock(_component_v_col, {
              key: 0,
              class: "py-0"
            }, {
              default: vue.withCtx(() => [
                vue.createElementVNode("div", _hoisted_2, vue.toDisplayString(_ctx.label), 1),
                vue.createVNode(_component_v_divider),
                _ctx.help && _ctx.showHelp ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_3, vue.toDisplayString(_ctx.help), 1)) : vue.createCommentVNode("", true)
              ]),
              _: 1
            })) : vue.createCommentVNode("", true)
          ]),
          _: 1
        }),
        _ctx.type != "proxy" ? (vue.openBlock(), vue.createBlock(_component_v_row, { key: 0 }, {
          default: vue.withCtx(() => [
            _ctx.size == 1 ? (vue.openBlock(), vue.createBlock(_component_v_col, {
              key: 0,
              class: "pt-0 pb-1"
            }, {
              default: vue.withCtx(() => [
                vue.createVNode(_component_v_text_field, {
                  name: `${_ctx.data().type}:${_ctx.name}:${_ctx.i}`,
                  "bg-color": _ctx.color(),
                  modelValue: _ctx.model,
                  "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => _ctx.model = $event),
                  label: _ctx.label,
                  hint: _ctx.help,
                  density: "compact",
                  rules: [_ctx.rule],
                  onBlur: _cache[2] || (_cache[2] = ($event) => _ctx.validate()),
                  onKeydown: _cache[3] || (_cache[3] = vue.withKeys(($event) => _ctx.validate(), ["enter"])),
                  "persistent-hint": _ctx.showHelp,
                  "hide-details": !_ctx.showHelp || !_ctx.help,
                  variant: "underlined",
                  disabled: _ctx.disabled || !_ctx.decorator.enable,
                  readonly: _ctx.readonly
                }, null, 8, ["name", "bg-color", "modelValue", "label", "hint", "rules", "persistent-hint", "hide-details", "disabled", "readonly"])
              ]),
              _: 1
            })) : vue.createCommentVNode("", true),
            _ctx.size != 1 ? (vue.openBlock(true), vue.createElementBlock(vue.Fragment, { key: 1 }, vue.renderList(_ctx.computedSize, (i) => {
              return vue.openBlock(), vue.createBlock(_component_v_col, vue.mergeProps({
                class: "py-1",
                key: i,
                ref_for: true
              }, _ctx.getComponentProps(i - 1)), {
                default: vue.withCtx(() => [
                  vue.createVNode(_component_v_row, {
                    "no-gutters": "",
                    class: "align-center"
                  }, {
                    default: vue.withCtx(() => [
                      vue.createVNode(_component_v_text_field, {
                        class: "mt-0",
                        name: `${_ctx.data().type}:${_ctx.name}:${i}`,
                        "bg-color": _ctx.color(i),
                        modelValue: _ctx.model[i - 1],
                        "onUpdate:modelValue": ($event) => _ctx.model[i - 1] = $event,
                        density: "compact",
                        rules: [_ctx.rule],
                        onBlur: ($event) => _ctx.validate(i),
                        onKeydown: vue.withKeys(($event) => _ctx.validate(i), ["enter"]),
                        "hide-details": "",
                        disabled: _ctx.disabled || !_ctx.decorator.enable,
                        readonly: _ctx.readonly,
                        variant: "underlined"
                      }, null, 8, ["name", "bg-color", "modelValue", "onUpdate:modelValue", "rules", "onBlur", "onKeydown", "disabled", "readonly"]),
                      _ctx.computedSizeControl ? (vue.openBlock(), vue.createBlock(_component_v_btn, {
                        key: 0,
                        class: "ml-2 elevation-0",
                        icon: "mdi-minus-circle-outline",
                        size: "x-small",
                        onClick: ($event) => _ctx.deleteEntry(i - 1),
                        disabled: _ctx.disabled || !_ctx.decorator.enable,
                        readonly: _ctx.readonly
                      }, null, 8, ["onClick", "disabled", "readonly"])) : vue.createCommentVNode("", true)
                    ]),
                    _: 2
                  }, 1024)
                ]),
                _: 2
              }, 1040);
            }), 128)) : vue.createCommentVNode("", true)
          ]),
          _: 1
        })) : vue.createCommentVNode("", true),
        _ctx.hints.length ? (vue.openBlock(), vue.createBlock(_component_v_col, {
          key: 1,
          class: "px-0 mt-1"
        }, {
          default: vue.withCtx(() => [
            (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(_ctx.hints, (hint, idx) => {
              return vue.openBlock(), vue.createBlock(_component_v_alert, {
                key: idx,
                class: "mb-1",
                type: _ctx.levelToType(hint.level),
                border: "start"
              }, {
                default: vue.withCtx(() => [
                  vue.createTextVNode(vue.toDisplayString(hint.message), 1)
                ]),
                _: 2
              }, 1032, ["type"]);
            }), 128))
          ]),
          _: 1
        })) : vue.createCommentVNode("", true)
      ]),
      _: 1
    }, 512)), [
      [vue.vShow, _ctx.shouldShow]
    ]);
  }
  const SwTextField = /* @__PURE__ */ _export_sfc(_sfc_main$5, [["render", render$5]]);
  const { computed: computed$3, inject: inject$3, toRef: toRef$1, ref: ref$1 } = window.Vue;
  const _sfc_main$4 = {
    name: "swProxy",
    props: {
      name: {
        type: String
      },
      mtime: {
        type: Number
      },
      size: {
        type: Number,
        default: 1
      },
      sizeControl: {
        type: Boolean,
        default: false
      },
      proxyType: {
        type: String
      }
    },
    components: {
      SimputInput
    },
    setup(props) {
      inject$3("data");
      const dirty = inject$3("dirty");
      const domains = inject$3("domains");
      const { decorator } = useDecorator({
        domains,
        mtime: toRef$1(props.mtime),
        name: toRef$1(props.name)
      });
      const properties = inject$3("properties");
      const model = computed$3({
        get() {
          props.mtime;
          const value = properties() && properties()[props.name];
          if (!value && props.size > 1) {
            const emptyArray = [];
            emptyArray.length = props.size;
            return emptyArray;
          }
          return value;
        },
        set(v) {
          properties()[props.name] = v;
        }
      });
      const itemId = computed$3(() => {
        props.mtime;
        return properties()[props.name];
      });
      const computedLayout = computed$3(() => {
        var _a, _b;
        props.mtime;
        return props.layout || ((_b = (_a = domains()[props.name]) == null ? void 0 : _a.UI) == null ? void 0 : _b.layout) || "vertical";
      });
      const computedSize = computed$3(() => {
        if (Number(props.size) !== 1) {
          return Math.max(props.size || 1, model.value.length || 0);
        }
        return Number(props.size);
      });
      const computedSizeControl = computed$3(() => {
        var _a, _b;
        props.mtime;
        return props.sizeControl || ((_b = (_a = domains()[props.name]) == null ? void 0 : _a.UI) == null ? void 0 : _b.sizeControl);
      });
      const deleteEntry = function deleteEntry2(index) {
        if (computedSize.value > Number(props.size)) {
          model.value.splice(index, 1);
          dirty(props.name);
        }
      };
      const getComponentProps = function getComponentProps2(index) {
        if (computedLayout.value === "vertical") {
          return { cols: 12 };
        }
        if (computedLayout.value === "l2") {
          return { cols: 6 };
        }
        if (computedLayout.value === "l3") {
          return { cols: 4 };
        }
        if (computedLayout.value === "l4") {
          return { cols: 3 };
        }
        if (computedLayout.value === "m3-half") {
          const attrs = { cols: 4 };
          if (index === 3) {
            attrs.offset = 4;
          }
          if (index === 5) {
            attrs.offset = 8;
          }
          return attrs;
        }
        return {};
      };
      return {
        itemId,
        decorator,
        model,
        computedLayout,
        computedSize,
        computedSizeControl,
        deleteEntry,
        getComponentProps
      };
    }
  };
  function render$4(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_SimputInput = vue.resolveComponent("SimputInput");
    const _component_v_col = vue.resolveComponent("v-col");
    const _component_v_btn = vue.resolveComponent("v-btn");
    const _component_v_row = vue.resolveComponent("v-row");
    return _ctx.size == 1 ? vue.withDirectives((vue.openBlock(), vue.createBlock(_component_SimputInput, {
      key: 0,
      itemId: _ctx.itemId
    }, null, 8, ["itemId"])), [
      [vue.vShow, _ctx.decorator.show]
    ]) : (vue.openBlock(), vue.createBlock(_component_v_col, { key: 1 }, {
      default: vue.withCtx(() => [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(_ctx.computedSize, (i) => {
          return vue.openBlock(), vue.createBlock(_component_v_row, vue.mergeProps({
            class: "py-1",
            key: i,
            ref_for: true
          }, _ctx.getComponentProps(i - 1)), {
            default: vue.withCtx(() => [
              vue.createVNode(_component_v_col, null, {
                default: vue.withCtx(() => [
                  vue.withDirectives(vue.createVNode(_component_SimputInput, {
                    itemId: _ctx.itemId[i - 1]
                  }, null, 8, ["itemId"]), [
                    [vue.vShow, _ctx.decorator.show]
                  ])
                ]),
                _: 2
              }, 1024),
              vue.createVNode(_component_v_col, { cols: "1" }, {
                default: vue.withCtx(() => [
                  _ctx.computedSizeControl ? (vue.openBlock(), vue.createBlock(_component_v_btn, {
                    key: 0,
                    class: "ml-2 elevation-0",
                    icon: "mdi-minus-circle-outline",
                    size: "x-small",
                    onClick: ($event) => _ctx.deleteEntry(i - 1)
                  }, null, 8, ["onClick"])) : vue.createCommentVNode("", true)
                ]),
                _: 2
              }, 1024)
            ]),
            _: 2
          }, 1040);
        }), 128))
      ]),
      _: 1
    }));
  }
  const SwProxy = /* @__PURE__ */ _export_sfc(_sfc_main$4, [["render", render$4]]);
  const { computed: computed$2, inject: inject$2 } = window.Vue;
  const _sfc_main$3 = {
    name: "swShow",
    props: {
      property: {
        type: String
      },
      domain: {
        type: String
      },
      mtime: {
        type: Number
      }
    },
    setup(props) {
      inject$2("properties");
      const domains = inject$2("domains");
      const visible = computed$2(() => {
        var _a, _b;
        this.mtime;
        const domain = (_b = (_a = domains()) == null ? void 0 : _a[props.property]) == null ? void 0 : _b[props.domain];
        if (!domain) {
          return true;
        }
        return domain.value.value;
      });
      return {
        visible
      };
    }
  };
  function render$3(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.withDirectives((vue.openBlock(), vue.createElementBlock("div", null, [
      vue.renderSlot(_ctx.$slots, "default")
    ], 512)), [
      [vue.vShow, _ctx.visible]
    ]);
  }
  const SwShow = /* @__PURE__ */ _export_sfc(_sfc_main$3, [["render", render$3]]);
  const { computed: computed$1, inject: inject$1 } = window.Vue;
  const _sfc_main$2 = {
    name: "swHide",
    props: {
      property: {
        type: String
      },
      domain: {
        type: String
      },
      mtime: {
        type: Number
      }
    },
    setup(props) {
      inject$1("properties");
      const domains = inject$1("domains");
      const visible = computed$1(() => {
        var _a, _b;
        this.mtime;
        const domain = (_b = (_a = domains()) == null ? void 0 : _a[props.property]) == null ? void 0 : _b[props.domain];
        if (!domain) {
          return false;
        }
        return !domain.value.value;
      });
      return {
        visible
      };
    }
  };
  function render$2(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.withDirectives((vue.openBlock(), vue.createElementBlock("div", null, [
      vue.renderSlot(_ctx.$slots, "default")
    ], 512)), [
      [vue.vShow, _ctx.visible]
    ]);
  }
  const SwHide = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["render", render$2]]);
  const _sfc_main$1 = {
    name: "swText",
    props: {
      content: {
        type: String
      }
    }
  };
  function render$1(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("div", null, vue.toDisplayString(_ctx.content), 1);
  }
  const SwText = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["render", render$1]]);
  const { ref, computed, onMounted, inject, useSlots, toRef } = window.Vue;
  const _sfc_main = {
    name: "swGroup",
    props: {
      title: {
        type: String
      },
      name: {
        type: String
      },
      mtime: {
        type: Number
      }
    },
    setup(props) {
      const mounted = ref(false);
      const domains = inject("domains");
      const slots = useSlots();
      const { decorator } = useDecorator({
        domains,
        mtime: toRef(props.mtime),
        name: toRef(props.name)
      });
      onMounted(() => mounted.value = true);
      const visible = computed(() => {
        props.mtime;
        mounted.value;
        if (decorator.value && !decorator.value.show && !decorator.value.query) {
          return false;
        }
        let visibleCount = 0;
        const helper = (vNode) => {
          var _a, _b, _c, _d;
          if (vNode.componentInstance == null) {
            (_a = vNode == null ? void 0 : vNode.children) == null ? void 0 : _a.forEach(helper);
          }
          const show = ((_b = vNode.componentInstance) == null ? void 0 : _b.shouldShow) || ((_d = (_c = vNode.componentInstance) == null ? void 0 : _c.decorator) == null ? void 0 : _d.show);
          if (show) {
            visibleCount++;
          }
        };
        slots.default().forEach(helper);
        return visibleCount > 0;
      });
      return {
        visible
      };
    }
  };
  const _hoisted_1 = { class: "text-h6 px-2" };
  function render(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_v_divider = vue.resolveComponent("v-divider");
    const _component_v_col = vue.resolveComponent("v-col");
    return vue.withDirectives((vue.openBlock(), vue.createBlock(_component_v_col, { class: "px-0" }, {
      default: vue.withCtx(() => [
        vue.createElementVNode("div", _hoisted_1, vue.toDisplayString(_ctx.title), 1),
        vue.createVNode(_component_v_divider, { class: "mb-2" }),
        vue.renderSlot(_ctx.$slots, "default")
      ]),
      _: 3
    }, 512)), [
      [vue.vShow, _ctx.visible]
    ]);
  }
  const SwGroup = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", render]]);
  const widgets = {
    SwSelect,
    SwSlider,
    SwSwitch,
    SwTextArea,
    SwTextField,
    SwProxy,
    SwShow,
    SwHide,
    SwText,
    SwGroup
  };
  function install(Vue) {
    Object.keys(components).forEach((name) => {
      Vue.component(name, components[name]);
    });
    Object.keys(widgets).forEach((name) => {
      Vue.component(name, widgets[name]);
    });
  }
  exports2.install = install;
  Object.defineProperty(exports2, Symbol.toStringTag, { value: "Module" });
});
