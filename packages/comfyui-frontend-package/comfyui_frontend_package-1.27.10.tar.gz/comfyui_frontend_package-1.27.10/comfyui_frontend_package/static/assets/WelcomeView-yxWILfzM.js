var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });
import { defineComponent, openBlock, createBlock, withCtx, createElementVNode, createVNode, unref } from "vue";
import { _ as _imports_0 } from "./comfy-brand-mark-XJkMJ9aQ.js";
import Button from "primevue/button";
import { cw as useRouter } from "./index-BKeTeXLp.js";
import { _ as _sfc_main$1 } from "./BaseViewTemplate-e9EU5LcP.js";
import "@primevue/themes";
import "@primevue/themes/aura";
import "primevue/config";
import "primevue/confirmationservice";
import "primevue/toastservice";
import "primevue/tooltip";
import "primevue/blockui";
import "primevue/progressspinner";
import "primevue/dialog";
import "vue-i18n";
import "primevue/scrollpanel";
import "primevue/skeleton";
import "primevue/checkbox";
import "primevue/message";
import "primevue/divider";
import "primevue/usetoast";
import "primevue/card";
import "primevue/listbox";
import "primevue/panel";
import "primevue/progressbar";
import "primevue/floatlabel";
import "primevue/inputtext";
import "@primevue/forms";
import "@primevue/forms/resolvers/zod";
import "primevue/password";
import "primevue/tag";
import "primevue/inputnumber";
import "primevue/popover";
import "primevue/toggleswitch";
import "primevue/tab";
import "primevue/tablist";
import "primevue/tabpanel";
import "primevue/tabpanels";
import "primevue/tabs";
import "primevue/multiselect";
import "primevue/autocomplete";
import "primevue/dropdown";
import "primevue/tabmenu";
import "primevue/dataview";
import "primevue/selectbutton";
import "primevue/column";
import "primevue/datatable";
import "primevue/iconfield";
import "primevue/inputicon";
import "primevue/badge";
import "primevue/chip";
import "primevue/select";
import "primevue/colorpicker";
import "primevue/radiobutton";
import "primevue/knob";
import "primevue/slider";
import "primevue/contextmenu";
import "primevue/tree";
import "primevue/toolbar";
import "primevue/confirmpopup";
import "primevue/useconfirm";
import "primevue/galleria";
import "primevue/confirmdialog";
const _hoisted_1 = { class: "flex items-center justify-center min-h-screen" };
const _hoisted_2 = { class: "grid grid-rows-2 gap-8" };
const _hoisted_3 = { class: "flex items-end justify-center" };
const _hoisted_4 = ["alt"];
const _hoisted_5 = { class: "flex flex-col items-center justify-center gap-4" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "WelcomeView",
  setup(__props) {
    const router = useRouter();
    const navigateTo = /* @__PURE__ */ __name(async (path) => {
      await router.push(path);
    }, "navigateTo");
    return (_ctx, _cache) => {
      return openBlock(), createBlock(_sfc_main$1, { dark: "" }, {
        default: withCtx(() => [
          createElementVNode("div", _hoisted_1, [
            createElementVNode("div", _hoisted_2, [
              createElementVNode("div", _hoisted_3, [
                createElementVNode("img", {
                  src: _imports_0,
                  alt: _ctx.$t("g.logoAlt"),
                  class: "w-60"
                }, null, 8, _hoisted_4)
              ]),
              createElementVNode("div", _hoisted_5, [
                createVNode(unref(Button), {
                  label: _ctx.$t("welcome.getStarted"),
                  class: "px-8 mt-4 bg-brand-yellow hover:bg-brand-yellow/90 border-0 rounded-lg transition-colors",
                  pt: {
                    label: { class: "font-inter text-neutral-900 font-black" }
                  },
                  onClick: _cache[0] || (_cache[0] = ($event) => navigateTo("/install"))
                }, null, 8, ["label"])
              ])
            ])
          ])
        ]),
        _: 1
      });
    };
  }
});
export {
  _sfc_main as default
};
//# sourceMappingURL=WelcomeView-yxWILfzM.js.map
