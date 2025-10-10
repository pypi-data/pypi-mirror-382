/*! For license information please see 3706.a402e2e1c1298deb.js.LICENSE.txt */
"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["3706"],{17711:function(e,t,i){i(35748),i(65315),i(22416),i(95013);var o=i(69868),r=i(84922),n=i(11991),a=i(90933);i(9974),i(95968);let s,l,d=e=>e;class c extends r.WF{get items(){var e;return null===(e=this._menu)||void 0===e?void 0:e.items}get selected(){var e;return null===(e=this._menu)||void 0===e?void 0:e.selected}focus(){var e,t;null!==(e=this._menu)&&void 0!==e&&e.open?this._menu.focusItemAtIndex(0):null===(t=this._triggerButton)||void 0===t||t.focus()}render(){return(0,r.qy)(s||(s=d`
      <div @click=${0}>
        <slot name="trigger" @slotchange=${0}></slot>
      </div>
      <ha-menu
        .corner=${0}
        .menuCorner=${0}
        .fixed=${0}
        .multi=${0}
        .activatable=${0}
        .y=${0}
        .x=${0}
      >
        <slot></slot>
      </ha-menu>
    `),this._handleClick,this._setTriggerAria,this.corner,this.menuCorner,this.fixed,this.multi,this.activatable,this.y,this.x)}firstUpdated(e){super.firstUpdated(e),"rtl"===a.G.document.dir&&this.updateComplete.then((()=>{this.querySelectorAll("ha-list-item").forEach((e=>{const t=document.createElement("style");t.innerHTML="span.material-icons:first-of-type { margin-left: var(--mdc-list-item-graphic-margin, 32px) !important; margin-right: 0px !important;}",e.shadowRoot.appendChild(t)}))}))}_handleClick(){this.disabled||(this._menu.anchor=this.noAnchor?null:this,this._menu.show())}get _triggerButton(){return this.querySelector('ha-icon-button[slot="trigger"], ha-button[slot="trigger"]')}_setTriggerAria(){this._triggerButton&&(this._triggerButton.ariaHasPopup="menu")}constructor(...e){super(...e),this.corner="BOTTOM_START",this.menuCorner="START",this.x=null,this.y=null,this.multi=!1,this.activatable=!1,this.disabled=!1,this.fixed=!1,this.noAnchor=!1}}c.styles=(0,r.AH)(l||(l=d`
    :host {
      display: inline-block;
      position: relative;
    }
    ::slotted([disabled]) {
      color: var(--disabled-text-color);
    }
  `)),(0,o.__decorate)([(0,n.MZ)()],c.prototype,"corner",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"menu-corner"})],c.prototype,"menuCorner",void 0),(0,o.__decorate)([(0,n.MZ)({type:Number})],c.prototype,"x",void 0),(0,o.__decorate)([(0,n.MZ)({type:Number})],c.prototype,"y",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],c.prototype,"multi",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],c.prototype,"activatable",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],c.prototype,"disabled",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],c.prototype,"fixed",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,attribute:"no-anchor"})],c.prototype,"noAnchor",void 0),(0,o.__decorate)([(0,n.P)("ha-menu",!0)],c.prototype,"_menu",void 0),c=(0,o.__decorate)([(0,n.EM)("ha-button-menu")],c)},26614:function(e,t,i){i(35748),i(5934),i(95013);var o=i(69868),r=i(83599),n=i(9625),a=i(57437),s=i(84922),l=i(11991),d=i(75907),c=i(73120);i(71978);let h,m,p=e=>e;class u extends r.h{async onChange(e){super.onChange(e),(0,c.r)(this,e.type)}render(){const e={"mdc-deprecated-list-item__graphic":this.left,"mdc-deprecated-list-item__meta":!this.left},t=this.renderText(),i=this.graphic&&"control"!==this.graphic&&!this.left?this.renderGraphic():s.s6,o=this.hasMeta&&this.left?this.renderMeta():s.s6,r=this.renderRipple();return(0,s.qy)(h||(h=p` ${0} ${0} ${0}
      <span class=${0}>
        <ha-checkbox
          reducedTouchTarget
          tabindex=${0}
          .checked=${0}
          .indeterminate=${0}
          ?disabled=${0}
          @change=${0}
        >
        </ha-checkbox>
      </span>
      ${0} ${0}`),r,i,this.left?"":t,(0,d.H)(e),this.tabindex,this.selected,this.indeterminate,this.disabled||this.checkboxDisabled,this.onChange,this.left?t:"",o)}constructor(...e){super(...e),this.checkboxDisabled=!1,this.indeterminate=!1}}u.styles=[a.R,n.R,(0,s.AH)(m||(m=p`
      :host {
        --mdc-theme-secondary: var(--primary-color);
      }

      :host([graphic="avatar"]) .mdc-deprecated-list-item__graphic,
      :host([graphic="medium"]) .mdc-deprecated-list-item__graphic,
      :host([graphic="large"]) .mdc-deprecated-list-item__graphic,
      :host([graphic="control"]) .mdc-deprecated-list-item__graphic {
        margin-inline-end: var(--mdc-list-item-graphic-margin, 16px);
        margin-inline-start: 0px;
        direction: var(--direction);
      }
      .mdc-deprecated-list-item__meta {
        flex-shrink: 0;
        direction: var(--direction);
        margin-inline-start: auto;
        margin-inline-end: 0;
      }
      .mdc-deprecated-list-item__graphic {
        margin-top: var(--check-list-item-graphic-margin-top);
      }
      :host([graphic="icon"]) .mdc-deprecated-list-item__graphic {
        margin-inline-start: 0;
        margin-inline-end: var(--mdc-list-item-graphic-margin, 32px);
      }
    `))],(0,o.__decorate)([(0,l.MZ)({type:Boolean,attribute:"checkbox-disabled"})],u.prototype,"checkboxDisabled",void 0),(0,o.__decorate)([(0,l.MZ)({type:Boolean})],u.prototype,"indeterminate",void 0),u=(0,o.__decorate)([(0,l.EM)("ha-check-list-item")],u)},99681:function(e,t,i){i.r(t),i.d(t,{HaFormMultiSelect:function(){return g}});i(37216),i(79827),i(35748),i(65315),i(837),i(84136),i(37089),i(18223),i(95013);var o=i(69868),r=i(84922),n=i(11991),a=i(73120);i(17711),i(26614),i(71978),i(52893),i(93672),i(11934),i(61647),i(70154);let s,l,d,c,h,m=e=>e;function p(e){return Array.isArray(e)?e[0]:e}function u(e){return Array.isArray(e)?e[1]||e[0]:e}class g extends r.WF{focus(){this._input&&this._input.focus()}render(){const e=Array.isArray(this.schema.options)?this.schema.options:Object.entries(this.schema.options),t=this.data||[];return e.length<6?(0,r.qy)(s||(s=m`<div>
        ${0}${0}
      </div> `),this.label,e.map((e=>{const i=p(e);return(0,r.qy)(l||(l=m`
            <ha-formfield .label=${0}>
              <ha-checkbox
                .checked=${0}
                .value=${0}
                .disabled=${0}
                @change=${0}
              ></ha-checkbox>
            </ha-formfield>
          `),u(e),t.includes(i),i,this.disabled,this._valueChanged)}))):(0,r.qy)(d||(d=m`
      <ha-md-button-menu
        .disabled=${0}
        @opening=${0}
        @closing=${0}
        positioning="fixed"
      >
        <ha-textfield
          slot="trigger"
          .label=${0}
          .value=${0}
          .disabled=${0}
          tabindex="-1"
        ></ha-textfield>
        <ha-icon-button
          slot="trigger"
          .label=${0}
          .path=${0}
        ></ha-icon-button>
        ${0}
      </ha-md-button-menu>
    `),this.disabled,this._handleOpen,this._handleClose,this.label,t.map((t=>u(e.find((e=>p(e)===t)))||t)).join(", "),this.disabled,this.label,this._opened?"M7,15L12,10L17,15H7Z":"M7,10L12,15L17,10H7Z",e.map((e=>{const i=p(e),o=t.includes(i);return(0,r.qy)(c||(c=m`<ha-md-menu-item
            type="option"
            aria-checked=${0}
            .value=${0}
            .action=${0}
            .activated=${0}
            @click=${0}
            @keydown=${0}
            keep-open
          >
            <ha-checkbox
              slot="start"
              tabindex="-1"
              .checked=${0}
            ></ha-checkbox>
            ${0}
          </ha-md-menu-item>`),o,i,o?"remove":"add",o,this._toggleItem,this._keydown,o,u(e))})))}_keydown(e){"Space"!==e.code&&"Enter"!==e.code||(e.preventDefault(),this._toggleItem(e))}_toggleItem(e){const t=this.data||[];let i;i="add"===e.currentTarget.action?[...t,e.currentTarget.value]:t.filter((t=>t!==e.currentTarget.value)),(0,a.r)(this,"value-changed",{value:i})}firstUpdated(){this.updateComplete.then((()=>{var e;const{formElement:t,mdcRoot:i}=(null===(e=this.shadowRoot)||void 0===e?void 0:e.querySelector("ha-textfield"))||{};t&&(t.style.textOverflow="ellipsis"),i&&(i.style.cursor="pointer")}))}updated(e){e.has("schema")&&this.toggleAttribute("own-margin",Object.keys(this.schema.options).length>=6&&!!this.schema.required)}_valueChanged(e){const{value:t,checked:i}=e.target;this._handleValueChanged(t,i)}_handleValueChanged(e,t){let i;if(t)if(this.data){if(this.data.includes(e))return;i=[...this.data,e]}else i=[e];else{if(!this.data.includes(e))return;i=this.data.filter((t=>t!==e))}(0,a.r)(this,"value-changed",{value:i})}_handleOpen(e){e.stopPropagation(),this._opened=!0,this.toggleAttribute("opened",!0)}_handleClose(e){e.stopPropagation(),this._opened=!1,this.toggleAttribute("opened",!1)}constructor(...e){super(...e),this.disabled=!1,this._opened=!1}}g.styles=(0,r.AH)(h||(h=m`
    :host([own-margin]) {
      margin-bottom: 5px;
    }
    ha-md-button-menu {
      display: block;
      cursor: pointer;
    }
    ha-formfield {
      display: block;
      padding-right: 16px;
      padding-inline-end: 16px;
      padding-inline-start: initial;
      direction: var(--direction);
    }
    ha-textfield {
      display: block;
      width: 100%;
      pointer-events: none;
    }
    ha-icon-button {
      color: var(--input-dropdown-icon-color);
      position: absolute;
      right: 1em;
      top: 4px;
      cursor: pointer;
      inset-inline-end: 1em;
      inset-inline-start: initial;
      direction: var(--direction);
    }
    :host([opened]) ha-icon-button {
      color: var(--primary-color);
    }
    :host([opened]) ha-md-button-menu {
      --mdc-text-field-idle-line-color: var(--input-hover-line-color);
      --mdc-text-field-label-ink-color: var(--primary-color);
    }
  `)),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],g.prototype,"schema",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],g.prototype,"data",void 0),(0,o.__decorate)([(0,n.MZ)()],g.prototype,"label",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],g.prototype,"disabled",void 0),(0,o.__decorate)([(0,n.wk)()],g.prototype,"_opened",void 0),(0,o.__decorate)([(0,n.P)("ha-button-menu")],g.prototype,"_input",void 0),g=(0,o.__decorate)([(0,n.EM)("ha-form-multi_select")],g)},61647:function(e,t,i){i(35748),i(95013);var o=i(69868),r=i(84922),n=i(11991),a=i(73120),s=(i(9974),i(5673)),l=i(89591),d=i(18396);let c;class h extends s.W1{connectedCallback(){super.connectedCallback(),this.addEventListener("close-menu",this._handleCloseMenu)}_handleCloseMenu(e){var t,i;e.detail.reason.kind===d.fi.KEYDOWN&&e.detail.reason.key===d.NV.ESCAPE||null===(t=(i=e.detail.initiator).clickAction)||void 0===t||t.call(i,e.detail.initiator)}}h.styles=[l.R,(0,r.AH)(c||(c=(e=>e)`
      :host {
        --md-sys-color-surface-container: var(--card-background-color);
      }
    `))],h=(0,o.__decorate)([(0,n.EM)("ha-md-menu")],h);let m,p,u=e=>e;class g extends r.WF{get items(){return this._menu.items}focus(){var e;this._menu.open?this._menu.focus():null===(e=this._triggerButton)||void 0===e||e.focus()}render(){return(0,r.qy)(m||(m=u`
      <div @click=${0}>
        <slot name="trigger" @slotchange=${0}></slot>
      </div>
      <ha-md-menu
        .quick=${0}
        .positioning=${0}
        .hasOverflow=${0}
        .anchorCorner=${0}
        .menuCorner=${0}
        @opening=${0}
        @closing=${0}
      >
        <slot></slot>
      </ha-md-menu>
    `),this._handleClick,this._setTriggerAria,this.quick,this.positioning,this.hasOverflow,this.anchorCorner,this.menuCorner,this._handleOpening,this._handleClosing)}_handleOpening(){(0,a.r)(this,"opening",void 0,{composed:!1})}_handleClosing(){(0,a.r)(this,"closing",void 0,{composed:!1})}_handleClick(){this.disabled||(this._menu.anchorElement=this,this._menu.open?this._menu.close():this._menu.show())}get _triggerButton(){return this.querySelector('ha-icon-button[slot="trigger"], ha-button[slot="trigger"], ha-assist-chip[slot="trigger"]')}_setTriggerAria(){this._triggerButton&&(this._triggerButton.ariaHasPopup="menu")}constructor(...e){super(...e),this.disabled=!1,this.anchorCorner="end-start",this.menuCorner="start-start",this.hasOverflow=!1,this.quick=!1}}g.styles=(0,r.AH)(p||(p=u`
    :host {
      display: inline-block;
      position: relative;
    }
    ::slotted([disabled]) {
      color: var(--disabled-text-color);
    }
  `)),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],g.prototype,"disabled",void 0),(0,o.__decorate)([(0,n.MZ)()],g.prototype,"positioning",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"anchor-corner"})],g.prototype,"anchorCorner",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"menu-corner"})],g.prototype,"menuCorner",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,attribute:"has-overflow"})],g.prototype,"hasOverflow",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],g.prototype,"quick",void 0),(0,o.__decorate)([(0,n.P)("ha-md-menu",!0)],g.prototype,"_menu",void 0),g=(0,o.__decorate)([(0,n.EM)("ha-md-button-menu")],g)},70154:function(e,t,i){var o=i(69868),r=i(45369),n=i(20808),a=i(84922),s=i(11991);let l;class d extends r.K{}d.styles=[n.R,(0,a.AH)(l||(l=(e=>e)`
      :host {
        --ha-icon-display: block;
        --md-sys-color-primary: var(--primary-text-color);
        --md-sys-color-on-primary: var(--primary-text-color);
        --md-sys-color-secondary: var(--secondary-text-color);
        --md-sys-color-surface: var(--card-background-color);
        --md-sys-color-on-surface: var(--primary-text-color);
        --md-sys-color-on-surface-variant: var(--secondary-text-color);
        --md-sys-color-secondary-container: rgba(
          var(--rgb-primary-color),
          0.15
        );
        --md-sys-color-on-secondary-container: var(--text-primary-color);
        --mdc-icon-size: 16px;

        --md-sys-color-on-primary-container: var(--primary-text-color);
        --md-sys-color-on-secondary-container: var(--primary-text-color);
        --md-menu-item-label-text-font: Roboto, sans-serif;
      }
      :host(.warning) {
        --md-menu-item-label-text-color: var(--error-color);
        --md-menu-item-leading-icon-color: var(--error-color);
      }
      ::slotted([slot="headline"]) {
        text-wrap: nowrap;
      }
    `))],(0,o.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"clickAction",void 0),d=(0,o.__decorate)([(0,s.EM)("ha-md-menu-item")],d)},83599:function(e,t,i){i.d(t,{h:function(){return g}});i(35748),i(5934),i(95013);var o=i(69868),r=i(11991),n=i(29332),a=i(77485);let s=class extends n.L{};s.styles=[a.R],s=(0,o.__decorate)([(0,r.EM)("mwc-checkbox")],s);var l=i(84922),d=i(75907),c=i(41188);let h,m,p,u=e=>e;class g extends c.J{render(){const e={"mdc-deprecated-list-item__graphic":this.left,"mdc-deprecated-list-item__meta":!this.left},t=this.renderText(),i=this.graphic&&"control"!==this.graphic&&!this.left?this.renderGraphic():(0,l.qy)(h||(h=u``)),o=this.hasMeta&&this.left?this.renderMeta():(0,l.qy)(m||(m=u``)),r=this.renderRipple();return(0,l.qy)(p||(p=u`
      ${0}
      ${0}
      ${0}
      <span class=${0}>
        <mwc-checkbox
            reducedTouchTarget
            tabindex=${0}
            .checked=${0}
            ?disabled=${0}
            @change=${0}>
        </mwc-checkbox>
      </span>
      ${0}
      ${0}`),r,i,this.left?"":t,(0,d.H)(e),this.tabindex,this.selected,this.disabled,this.onChange,this.left?t:"",o)}async onChange(e){const t=e.target;this.selected===t.checked||(this._skipPropRequest=!0,this.selected=t.checked,await this.updateComplete,this._skipPropRequest=!1)}constructor(){super(...arguments),this.left=!1,this.graphic="control"}}(0,o.__decorate)([(0,r.P)("slot")],g.prototype,"slotElement",void 0),(0,o.__decorate)([(0,r.P)("mwc-checkbox")],g.prototype,"checkboxElement",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],g.prototype,"left",void 0),(0,o.__decorate)([(0,r.MZ)({type:String,reflect:!0})],g.prototype,"graphic",void 0)},9625:function(e,t,i){i.d(t,{R:function(){return r}});let o;const r=(0,i(84922).AH)(o||(o=(e=>e)`:host(:not([twoline])){height:56px}:host(:not([left])) .mdc-deprecated-list-item__meta{height:40px;width:40px}`))},48521:function(e,t,i){i.d(t,{X:function(){return r}});i(37216),i(99342),i(65315),i(22416),i(39118);var o=i(18396);class r{get typeaheadText(){if(null!==this.internalTypeaheadText)return this.internalTypeaheadText;const e=this.getHeadlineElements(),t=[];return e.forEach((e=>{e.textContent&&e.textContent.trim()&&t.push(e.textContent.trim())})),0===t.length&&this.getDefaultElements().forEach((e=>{e.textContent&&e.textContent.trim()&&t.push(e.textContent.trim())})),0===t.length&&this.getSupportingTextElements().forEach((e=>{e.textContent&&e.textContent.trim()&&t.push(e.textContent.trim())})),t.join(" ")}get tagName(){switch(this.host.type){case"link":return"a";case"button":return"button";default:return"li"}}get role(){return"option"===this.host.type?"option":"menuitem"}hostConnected(){this.host.toggleAttribute("md-menu-item",!0)}hostUpdate(){this.host.href&&(this.host.type="link")}setTypeaheadText(e){this.internalTypeaheadText=e}constructor(e,t){this.host=e,this.internalTypeaheadText=null,this.onClick=()=>{this.host.keepOpen||this.host.dispatchEvent((0,o.xr)(this.host,{kind:o.fi.CLICK_SELECTION}))},this.onKeydown=e=>{if(this.host.href&&"Enter"===e.code){const e=this.getInteractiveElement();e instanceof HTMLAnchorElement&&e.click()}if(e.defaultPrevented)return;const t=e.code;this.host.keepOpen&&"Escape"!==t||(0,o.Rb)(t)&&(e.preventDefault(),this.host.dispatchEvent((0,o.xr)(this.host,{kind:o.fi.KEYDOWN,key:t})))},this.getHeadlineElements=t.getHeadlineElements,this.getSupportingTextElements=t.getSupportingTextElements,this.getDefaultElements=t.getDefaultElements,this.getInteractiveElement=t.getInteractiveElement,this.host.addController(this)}}},20808:function(e,t,i){i.d(t,{R:function(){return r}});let o;const r=(0,i(84922).AH)(o||(o=(e=>e)`:host{display:flex;--md-ripple-hover-color: var(--md-menu-item-hover-state-layer-color, var(--md-sys-color-on-surface, #1d1b20));--md-ripple-hover-opacity: var(--md-menu-item-hover-state-layer-opacity, 0.08);--md-ripple-pressed-color: var(--md-menu-item-pressed-state-layer-color, var(--md-sys-color-on-surface, #1d1b20));--md-ripple-pressed-opacity: var(--md-menu-item-pressed-state-layer-opacity, 0.12)}:host([disabled]){opacity:var(--md-menu-item-disabled-opacity, 0.3);pointer-events:none}md-focus-ring{z-index:1;--md-focus-ring-shape: 8px}a,button,li{background:none;border:none;padding:0;margin:0;text-align:unset;text-decoration:none}.list-item{border-radius:inherit;display:flex;flex:1;max-width:inherit;min-width:inherit;outline:none;-webkit-tap-highlight-color:rgba(0,0,0,0)}.list-item:not(.disabled){cursor:pointer}[slot=container]{pointer-events:none}md-ripple{border-radius:inherit}md-item{border-radius:inherit;flex:1;color:var(--md-menu-item-label-text-color, var(--md-sys-color-on-surface, #1d1b20));font-family:var(--md-menu-item-label-text-font, var(--md-sys-typescale-body-large-font, var(--md-ref-typeface-plain, Roboto)));font-size:var(--md-menu-item-label-text-size, var(--md-sys-typescale-body-large-size, 1rem));line-height:var(--md-menu-item-label-text-line-height, var(--md-sys-typescale-body-large-line-height, 1.5rem));font-weight:var(--md-menu-item-label-text-weight, var(--md-sys-typescale-body-large-weight, var(--md-ref-typeface-weight-regular, 400)));min-height:var(--md-menu-item-one-line-container-height, 56px);padding-top:var(--md-menu-item-top-space, 12px);padding-bottom:var(--md-menu-item-bottom-space, 12px);padding-inline-start:var(--md-menu-item-leading-space, 16px);padding-inline-end:var(--md-menu-item-trailing-space, 16px)}md-item[multiline]{min-height:var(--md-menu-item-two-line-container-height, 72px)}[slot=supporting-text]{color:var(--md-menu-item-supporting-text-color, var(--md-sys-color-on-surface-variant, #49454f));font-family:var(--md-menu-item-supporting-text-font, var(--md-sys-typescale-body-medium-font, var(--md-ref-typeface-plain, Roboto)));font-size:var(--md-menu-item-supporting-text-size, var(--md-sys-typescale-body-medium-size, 0.875rem));line-height:var(--md-menu-item-supporting-text-line-height, var(--md-sys-typescale-body-medium-line-height, 1.25rem));font-weight:var(--md-menu-item-supporting-text-weight, var(--md-sys-typescale-body-medium-weight, var(--md-ref-typeface-weight-regular, 400)))}[slot=trailing-supporting-text]{color:var(--md-menu-item-trailing-supporting-text-color, var(--md-sys-color-on-surface-variant, #49454f));font-family:var(--md-menu-item-trailing-supporting-text-font, var(--md-sys-typescale-label-small-font, var(--md-ref-typeface-plain, Roboto)));font-size:var(--md-menu-item-trailing-supporting-text-size, var(--md-sys-typescale-label-small-size, 0.6875rem));line-height:var(--md-menu-item-trailing-supporting-text-line-height, var(--md-sys-typescale-label-small-line-height, 1rem));font-weight:var(--md-menu-item-trailing-supporting-text-weight, var(--md-sys-typescale-label-small-weight, var(--md-ref-typeface-weight-medium, 500)))}:is([slot=start],[slot=end])::slotted(*){fill:currentColor}[slot=start]{color:var(--md-menu-item-leading-icon-color, var(--md-sys-color-on-surface-variant, #49454f))}[slot=end]{color:var(--md-menu-item-trailing-icon-color, var(--md-sys-color-on-surface-variant, #49454f))}.list-item{background-color:var(--md-menu-item-container-color, transparent)}.list-item.selected{background-color:var(--md-menu-item-selected-container-color, var(--md-sys-color-secondary-container, #e8def8))}.selected:not(.disabled) ::slotted(*){color:var(--md-menu-item-selected-label-text-color, var(--md-sys-color-on-secondary-container, #1d192b))}@media(forced-colors: active){:host([disabled]),:host([disabled]) slot{color:GrayText;opacity:1}.list-item{position:relative}.list-item.selected::before{content:"";position:absolute;inset:0;box-sizing:border-box;border-radius:inherit;pointer-events:none;border:3px double CanvasText}}
`))},45369:function(e,t,i){i.d(t,{K:function(){return f}});i(35748),i(12977),i(95013);var o=i(69868),r=(i(36265),i(3275),i(61640),i(84922)),n=i(11991),a=i(75907),s=i(37523),l=i(78892),d=i(48521);let c,h,m,p,u,g,y,v,_=e=>e;const b=(0,l.n)(r.WF);class f extends b{get typeaheadText(){return this.menuItemController.typeaheadText}set typeaheadText(e){this.menuItemController.setTypeaheadText(e)}render(){return this.renderListItem((0,r.qy)(c||(c=_`
      <md-item>
        <div slot="container">
          ${0} ${0}
        </div>
        <slot name="start" slot="start"></slot>
        <slot name="end" slot="end"></slot>
        ${0}
      </md-item>
    `),this.renderRipple(),this.renderFocusRing(),this.renderBody()))}renderListItem(e){const t="link"===this.type;let i;switch(this.menuItemController.tagName){case"a":i=(0,s.eu)(h||(h=_`a`));break;case"button":i=(0,s.eu)(m||(m=_`button`));break;default:i=(0,s.eu)(p||(p=_`li`))}const o=t&&this.target?this.target:r.s6;return(0,s.qy)(u||(u=_`
      <${0}
        id="item"
        tabindex=${0}
        role=${0}
        aria-label=${0}
        aria-selected=${0}
        aria-checked=${0}
        aria-expanded=${0}
        aria-haspopup=${0}
        class="list-item ${0}"
        href=${0}
        target=${0}
        @click=${0}
        @keydown=${0}
      >${0}</${0}>
    `),i,this.disabled&&!t?-1:0,this.menuItemController.role,this.ariaLabel||r.s6,this.ariaSelected||r.s6,this.ariaChecked||r.s6,this.ariaExpanded||r.s6,this.ariaHasPopup||r.s6,(0,a.H)(this.getRenderClasses()),this.href||r.s6,o,this.menuItemController.onClick,this.menuItemController.onKeydown,e,i)}renderRipple(){return(0,r.qy)(g||(g=_` <md-ripple
      part="ripple"
      for="item"
      ?disabled=${0}></md-ripple>`),this.disabled)}renderFocusRing(){return(0,r.qy)(y||(y=_` <md-focus-ring
      part="focus-ring"
      for="item"
      inward></md-focus-ring>`))}getRenderClasses(){return{disabled:this.disabled,selected:this.selected}}renderBody(){return(0,r.qy)(v||(v=_`
      <slot></slot>
      <slot name="overline" slot="overline"></slot>
      <slot name="headline" slot="headline"></slot>
      <slot name="supporting-text" slot="supporting-text"></slot>
      <slot
        name="trailing-supporting-text"
        slot="trailing-supporting-text"></slot>
    `))}focus(){var e;null===(e=this.listItemRoot)||void 0===e||e.focus()}constructor(){super(...arguments),this.disabled=!1,this.type="menuitem",this.href="",this.target="",this.keepOpen=!1,this.selected=!1,this.menuItemController=new d.X(this,{getHeadlineElements:()=>this.headlineElements,getSupportingTextElements:()=>this.supportingTextElements,getDefaultElements:()=>this.defaultElements,getInteractiveElement:()=>this.listItemRoot})}}f.shadowRootOptions=Object.assign(Object.assign({},r.WF.shadowRootOptions),{},{delegatesFocus:!0}),(0,o.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],f.prototype,"disabled",void 0),(0,o.__decorate)([(0,n.MZ)()],f.prototype,"type",void 0),(0,o.__decorate)([(0,n.MZ)()],f.prototype,"href",void 0),(0,o.__decorate)([(0,n.MZ)()],f.prototype,"target",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,attribute:"keep-open"})],f.prototype,"keepOpen",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],f.prototype,"selected",void 0),(0,o.__decorate)([(0,n.P)(".list-item")],f.prototype,"listItemRoot",void 0),(0,o.__decorate)([(0,n.KN)({slot:"headline"})],f.prototype,"headlineElements",void 0),(0,o.__decorate)([(0,n.KN)({slot:"supporting-text"})],f.prototype,"supportingTextElements",void 0),(0,o.__decorate)([(0,n.gZ)({slot:""})],f.prototype,"defaultElements",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"typeahead-text"})],f.prototype,"typeaheadText",null)}}]);
//# sourceMappingURL=3706.a402e2e1c1298deb.js.map