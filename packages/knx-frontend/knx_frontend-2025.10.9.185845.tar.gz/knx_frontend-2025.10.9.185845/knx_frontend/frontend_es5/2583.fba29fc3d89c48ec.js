"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2583"],{23749:function(o,t,a){a.r(t);a(35748),a(95013);var r=a(69868),e=a(84922),i=a(11991),n=a(75907),l=a(73120);a(93672),a(95635);let s,c,d,h,u=o=>o;const p={info:"M11,9H13V7H11M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,17H13V11H11V17Z",warning:"M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16",error:"M11,15H13V17H11V15M11,7H13V13H11V7M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20Z",success:"M20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4C12.76,4 13.5,4.11 14.2,4.31L15.77,2.74C14.61,2.26 13.34,2 12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12M7.91,10.08L6.5,11.5L11,16L21,6L19.59,4.58L11,13.17L7.91,10.08Z"};class v extends e.WF{render(){return(0,e.qy)(s||(s=u`
      <div
        class="issue-type ${0}"
        role="alert"
      >
        <div class="icon ${0}">
          <slot name="icon">
            <ha-svg-icon .path=${0}></ha-svg-icon>
          </slot>
        </div>
        <div class=${0}>
          <div class="main-content">
            ${0}
            <slot></slot>
          </div>
          <div class="action">
            <slot name="action">
              ${0}
            </slot>
          </div>
        </div>
      </div>
    `),(0,n.H)({[this.alertType]:!0}),this.title?"":"no-title",p[this.alertType],(0,n.H)({content:!0,narrow:this.narrow}),this.title?(0,e.qy)(c||(c=u`<div class="title">${0}</div>`),this.title):e.s6,this.dismissable?(0,e.qy)(d||(d=u`<ha-icon-button
                    @click=${0}
                    label="Dismiss alert"
                    .path=${0}
                  ></ha-icon-button>`),this._dismissClicked,"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"):e.s6)}_dismissClicked(){(0,l.r)(this,"alert-dismissed-clicked")}constructor(...o){super(...o),this.title="",this.alertType="info",this.dismissable=!1,this.narrow=!1}}v.styles=(0,e.AH)(h||(h=u`
    .issue-type {
      position: relative;
      padding: 8px;
      display: flex;
    }
    .icon {
      height: var(--ha-alert-icon-size, 24px);
      width: var(--ha-alert-icon-size, 24px);
    }
    .issue-type::after {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      opacity: 0.12;
      pointer-events: none;
      content: "";
      border-radius: 4px;
    }
    .icon.no-title {
      align-self: center;
    }
    .content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      text-align: var(--float-start);
    }
    .content.narrow {
      flex-direction: column;
      align-items: flex-end;
    }
    .action {
      z-index: 1;
      width: min-content;
      --mdc-theme-primary: var(--primary-text-color);
    }
    .main-content {
      overflow-wrap: anywhere;
      word-break: break-word;
      line-height: normal;
      margin-left: 8px;
      margin-right: 0;
      margin-inline-start: 8px;
      margin-inline-end: 8px;
    }
    .title {
      margin-top: 2px;
      font-weight: var(--ha-font-weight-bold);
    }
    .action ha-icon-button {
      --mdc-theme-primary: var(--primary-text-color);
      --mdc-icon-button-size: 36px;
    }
    .issue-type.info > .icon {
      color: var(--info-color);
    }
    .issue-type.info::after {
      background-color: var(--info-color);
    }

    .issue-type.warning > .icon {
      color: var(--warning-color);
    }
    .issue-type.warning::after {
      background-color: var(--warning-color);
    }

    .issue-type.error > .icon {
      color: var(--error-color);
    }
    .issue-type.error::after {
      background-color: var(--error-color);
    }

    .issue-type.success > .icon {
      color: var(--success-color);
    }
    .issue-type.success::after {
      background-color: var(--success-color);
    }
    :host ::slotted(ul) {
      margin: 0;
      padding-inline-start: 20px;
    }
  `)),(0,r.__decorate)([(0,i.MZ)()],v.prototype,"title",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:"alert-type"})],v.prototype,"alertType",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean})],v.prototype,"dismissable",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean})],v.prototype,"narrow",void 0),v=(0,r.__decorate)([(0,i.EM)("ha-alert")],v)},76943:function(o,t,a){a.a(o,(async function(o,t){try{a(35748),a(95013);var r=a(69868),e=a(60498),i=a(84922),n=a(11991),l=o([e]);e=(l.then?(await l)():l)[0];let s,c=o=>o;class d extends e.A{static get styles(){return[e.A.styles,(0,i.AH)(s||(s=c`
        .button {
          /* set theme vars */
          --wa-form-control-padding-inline: 16px;
          --wa-font-weight-action: var(--ha-font-weight-medium);
          --wa-form-control-border-radius: var(
            --ha-button-border-radius,
            var(--ha-border-radius-pill)
          );

          --wa-form-control-height: var(
            --ha-button-height,
            var(--button-height, 40px)
          );

          font-size: var(--ha-font-size-m);
          line-height: 1;

          transition: background-color 0.15s ease-in-out;
        }

        :host([size="small"]) .button {
          --wa-form-control-height: var(
            --ha-button-height,
            var(--button-height, 32px)
          );
          font-size: var(--wa-font-size-s, var(--ha-font-size-m));
          --wa-form-control-padding-inline: 12px;
        }

        :host([variant="brand"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-primary-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-primary-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-primary-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-primary-loud-hover
          );
        }

        :host([variant="neutral"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-neutral-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-neutral-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-neutral-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-neutral-loud-hover
          );
        }

        :host([variant="success"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-success-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-success-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-success-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-success-loud-hover
          );
        }

        :host([variant="warning"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-warning-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-warning-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-warning-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-warning-loud-hover
          );
        }

        :host([variant="danger"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-danger-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-danger-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-danger-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-danger-loud-hover
          );
        }

        :host([appearance~="plain"]) .button {
          color: var(--wa-color-on-normal);
          background-color: transparent;
        }
        :host([appearance~="plain"]) .button.disabled {
          background-color: transparent;
          color: var(--ha-color-on-disabled-quiet);
        }

        :host([appearance~="outlined"]) .button.disabled {
          background-color: transparent;
          color: var(--ha-color-on-disabled-quiet);
        }

        @media (hover: hover) {
          :host([appearance~="filled"])
            .button:not(.disabled):not(.loading):hover {
            background-color: var(--button-color-fill-normal-hover);
          }
          :host([appearance~="accent"])
            .button:not(.disabled):not(.loading):hover {
            background-color: var(--button-color-fill-loud-hover);
          }
          :host([appearance~="plain"])
            .button:not(.disabled):not(.loading):hover {
            color: var(--wa-color-on-normal);
          }
        }
        :host([appearance~="filled"]) .button {
          color: var(--wa-color-on-normal);
          background-color: var(--wa-color-fill-normal);
          border-color: transparent;
        }
        :host([appearance~="filled"])
          .button:not(.disabled):not(.loading):active {
          background-color: var(--button-color-fill-normal-active);
        }
        :host([appearance~="filled"]) .button.disabled {
          background-color: var(--ha-color-fill-disabled-normal-resting);
          color: var(--ha-color-on-disabled-normal);
        }

        :host([appearance~="accent"]) .button {
          background-color: var(
            --wa-color-fill-loud,
            var(--wa-color-neutral-fill-loud)
          );
        }
        :host([appearance~="accent"])
          .button:not(.disabled):not(.loading):active {
          background-color: var(--button-color-fill-loud-active);
        }
        :host([appearance~="accent"]) .button.disabled {
          background-color: var(--ha-color-fill-disabled-loud-resting);
          color: var(--ha-color-on-disabled-loud);
        }

        :host([loading]) {
          pointer-events: none;
        }

        .button.disabled {
          opacity: 1;
        }

        slot[name="start"]::slotted(*) {
          margin-inline-end: 4px;
        }
        slot[name="end"]::slotted(*) {
          margin-inline-start: 4px;
        }

        .button.has-start {
          padding-inline-start: 8px;
        }
        .button.has-end {
          padding-inline-end: 8px;
        }
      `))]}constructor(...o){super(...o),this.variant="brand"}}d=(0,r.__decorate)([(0,n.EM)("ha-button")],d),t()}catch(s){t(s)}}))},8101:function(o,t,a){a.r(t),a.d(t,{HaIconButtonArrowPrev:function(){return c}});a(35748),a(95013);var r=a(69868),e=a(84922),i=a(11991),n=a(90933);a(93672);let l,s=o=>o;class c extends e.WF{render(){var o;return(0,e.qy)(l||(l=s`
      <ha-icon-button
        .disabled=${0}
        .label=${0}
        .path=${0}
      ></ha-icon-button>
    `),this.disabled,this.label||(null===(o=this.hass)||void 0===o?void 0:o.localize("ui.common.back"))||"Back",this._icon)}constructor(...o){super(...o),this.disabled=!1,this._icon="rtl"===n.G.document.dir?"M4,11V13H16L10.5,18.5L11.92,19.92L19.84,12L11.92,4.08L10.5,5.5L16,11H4Z":"M20,11V13H8L13.5,18.5L12.08,19.92L4.16,12L12.08,4.08L13.5,5.5L8,11H20Z"}}(0,r.__decorate)([(0,i.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean})],c.prototype,"disabled",void 0),(0,r.__decorate)([(0,i.MZ)()],c.prototype,"label",void 0),(0,r.__decorate)([(0,i.wk)()],c.prototype,"_icon",void 0),c=(0,r.__decorate)([(0,i.EM)("ha-icon-button-arrow-prev")],c)},93672:function(o,t,a){a.r(t),a.d(t,{HaIconButton:function(){return u}});a(35748),a(95013);var r=a(69868),e=(a(31807),a(84922)),i=a(11991),n=a(13802);a(95635);let l,s,c,d,h=o=>o;class u extends e.WF{focus(){var o;null===(o=this._button)||void 0===o||o.focus()}render(){return(0,e.qy)(l||(l=h`
      <mwc-icon-button
        aria-label=${0}
        title=${0}
        aria-haspopup=${0}
        .disabled=${0}
      >
        ${0}
      </mwc-icon-button>
    `),(0,n.J)(this.label),(0,n.J)(this.hideTitle?void 0:this.label),(0,n.J)(this.ariaHasPopup),this.disabled,this.path?(0,e.qy)(s||(s=h`<ha-svg-icon .path=${0}></ha-svg-icon>`),this.path):(0,e.qy)(c||(c=h`<slot></slot>`)))}constructor(...o){super(...o),this.disabled=!1,this.hideTitle=!1}}u.shadowRootOptions={mode:"open",delegatesFocus:!0},u.styles=(0,e.AH)(d||(d=h`
    :host {
      display: inline-block;
      outline: none;
    }
    :host([disabled]) {
      pointer-events: none;
    }
    mwc-icon-button {
      --mdc-theme-on-primary: currentColor;
      --mdc-theme-text-disabled-on-light: var(--disabled-text-color);
    }
  `)),(0,r.__decorate)([(0,i.MZ)({type:Boolean,reflect:!0})],u.prototype,"disabled",void 0),(0,r.__decorate)([(0,i.MZ)({type:String})],u.prototype,"path",void 0),(0,r.__decorate)([(0,i.MZ)({type:String})],u.prototype,"label",void 0),(0,r.__decorate)([(0,i.MZ)({type:String,attribute:"aria-haspopup"})],u.prototype,"ariaHasPopup",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:"hide-title",type:Boolean})],u.prototype,"hideTitle",void 0),(0,r.__decorate)([(0,i.P)("mwc-icon-button",!0)],u.prototype,"_button",void 0),u=(0,r.__decorate)([(0,i.EM)("ha-icon-button")],u)},3433:function(o,t,a){a(46852),a(35748),a(95013);var r=a(69868),e=a(84922),i=a(11991),n=a(73120);a(12977);class l{processMessage(o){if("removed"===o.type)for(const t of Object.keys(o.notifications))delete this.notifications[t];else this.notifications=Object.assign(Object.assign({},this.notifications),o.notifications);return Object.values(this.notifications)}constructor(){this.notifications={}}}a(93672);let s,c,d,h=o=>o;class u extends e.WF{connectedCallback(){super.connectedCallback(),this._attachNotifOnConnect&&(this._attachNotifOnConnect=!1,this._subscribeNotifications())}disconnectedCallback(){super.disconnectedCallback(),this._unsubNotifications&&(this._attachNotifOnConnect=!0,this._unsubNotifications(),this._unsubNotifications=void 0)}render(){if(!this._show)return e.s6;const o=this._hasNotifications&&(this.narrow||"always_hidden"===this.hass.dockedSidebar);return(0,e.qy)(s||(s=h`
      <ha-icon-button
        .label=${0}
        .path=${0}
        @click=${0}
      ></ha-icon-button>
      ${0}
    `),this.hass.localize("ui.sidebar.sidebar_toggle"),"M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z",this._toggleMenu,o?(0,e.qy)(c||(c=h`<div class="dot"></div>`)):"")}firstUpdated(o){super.firstUpdated(o),this.hassio&&(this._alwaysVisible=(Number(window.parent.frontendVersion)||0)<20190710)}willUpdate(o){if(super.willUpdate(o),!o.has("narrow")&&!o.has("hass"))return;const t=o.has("hass")?o.get("hass"):this.hass,a=(o.has("narrow")?o.get("narrow"):this.narrow)||"always_hidden"===(null==t?void 0:t.dockedSidebar),r=this.narrow||"always_hidden"===this.hass.dockedSidebar;this.hasUpdated&&a===r||(this._show=r||this._alwaysVisible,r?this._subscribeNotifications():this._unsubNotifications&&(this._unsubNotifications(),this._unsubNotifications=void 0))}_subscribeNotifications(){if(this._unsubNotifications)throw new Error("Already subscribed");this._unsubNotifications=((o,t)=>{const a=new l,r=o.subscribeMessage((o=>t(a.processMessage(o))),{type:"persistent_notification/subscribe"});return()=>{r.then((o=>null==o?void 0:o()))}})(this.hass.connection,(o=>{this._hasNotifications=o.length>0}))}_toggleMenu(){(0,n.r)(this,"hass-toggle-menu")}constructor(...o){super(...o),this.hassio=!1,this.narrow=!1,this._hasNotifications=!1,this._show=!1,this._alwaysVisible=!1,this._attachNotifOnConnect=!1}}u.styles=(0,e.AH)(d||(d=h`
    :host {
      position: relative;
    }
    .dot {
      pointer-events: none;
      position: absolute;
      background-color: var(--accent-color);
      width: 12px;
      height: 12px;
      top: 9px;
      right: 7px;
      inset-inline-end: 7px;
      inset-inline-start: initial;
      border-radius: 50%;
      border: 2px solid var(--app-header-background-color);
    }
  `)),(0,r.__decorate)([(0,i.MZ)({type:Boolean})],u.prototype,"hassio",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean})],u.prototype,"narrow",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,r.__decorate)([(0,i.wk)()],u.prototype,"_hasNotifications",void 0),(0,r.__decorate)([(0,i.wk)()],u.prototype,"_show",void 0),u=(0,r.__decorate)([(0,i.EM)("ha-menu-button")],u)},95635:function(o,t,a){a.r(t),a.d(t,{HaSvgIcon:function(){return h}});var r=a(69868),e=a(84922),i=a(11991);let n,l,s,c,d=o=>o;class h extends e.WF{render(){return(0,e.JW)(n||(n=d`
    <svg
      viewBox=${0}
      preserveAspectRatio="xMidYMid meet"
      focusable="false"
      role="img"
      aria-hidden="true"
    >
      <g>
        ${0}
        ${0}
      </g>
    </svg>`),this.viewBox||"0 0 24 24",this.path?(0,e.JW)(l||(l=d`<path class="primary-path" d=${0}></path>`),this.path):e.s6,this.secondaryPath?(0,e.JW)(s||(s=d`<path class="secondary-path" d=${0}></path>`),this.secondaryPath):e.s6)}}h.styles=(0,e.AH)(c||(c=d`
    :host {
      display: var(--ha-icon-display, inline-flex);
      align-items: center;
      justify-content: center;
      position: relative;
      vertical-align: middle;
      fill: var(--icon-primary-color, currentcolor);
      width: var(--mdc-icon-size, 24px);
      height: var(--mdc-icon-size, 24px);
    }
    svg {
      width: 100%;
      height: 100%;
      pointer-events: none;
      display: block;
    }
    path.primary-path {
      opacity: var(--icon-primary-opactity, 1);
    }
    path.secondary-path {
      fill: var(--icon-secondary-color, currentcolor);
      opacity: var(--icon-secondary-opactity, 0.5);
    }
  `)),(0,r.__decorate)([(0,i.MZ)()],h.prototype,"path",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:!1})],h.prototype,"secondaryPath",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:!1})],h.prototype,"viewBox",void 0),h=(0,r.__decorate)([(0,i.EM)("ha-svg-icon")],h)},18177:function(o,t,a){a.a(o,(async function(o,r){try{a.r(t);a(35748),a(95013);var e=a(69868),i=a(84922),n=a(11991),l=a(68985),s=(a(8101),a(76943)),c=(a(3433),a(23749),o([s]));s=(c.then?(await c)():c)[0];let d,h,u,p,v,b=o=>o;class f extends i.WF{render(){var o,t;return(0,i.qy)(d||(d=b`
      ${0}
      <div class="content">
        <ha-alert alert-type="error">${0}</ha-alert>
        <slot>
          <ha-button appearance="plain" size="small" @click=${0}>
            ${0}
          </ha-button>
        </slot>
      </div>
    `),this.toolbar?(0,i.qy)(h||(h=b`<div class="toolbar">
            ${0}
          </div>`),this.rootnav||null!==(o=history.state)&&void 0!==o&&o.root?(0,i.qy)(u||(u=b`
                  <ha-menu-button
                    .hass=${0}
                    .narrow=${0}
                  ></ha-menu-button>
                `),this.hass,this.narrow):(0,i.qy)(p||(p=b`
                  <ha-icon-button-arrow-prev
                    .hass=${0}
                    @click=${0}
                  ></ha-icon-button-arrow-prev>
                `),this.hass,this._handleBack)):"",this.error,this._handleBack,null===(t=this.hass)||void 0===t?void 0:t.localize("ui.common.back"))}_handleBack(){(0,l.O)()}static get styles(){return[(0,i.AH)(v||(v=b`
        :host {
          display: block;
          height: 100%;
          background-color: var(--primary-background-color);
        }
        .toolbar {
          display: flex;
          align-items: center;
          font-size: var(--ha-font-size-xl);
          height: var(--header-height);
          padding: 8px 12px;
          pointer-events: none;
          background-color: var(--app-header-background-color);
          font-weight: var(--ha-font-weight-normal);
          color: var(--app-header-text-color, white);
          border-bottom: var(--app-header-border-bottom, none);
          box-sizing: border-box;
        }
        @media (max-width: 599px) {
          .toolbar {
            padding: 4px;
          }
        }
        ha-icon-button-arrow-prev {
          pointer-events: auto;
        }
        .content {
          color: var(--primary-text-color);
          height: calc(100% - var(--header-height));
          display: flex;
          padding: 16px;
          align-items: center;
          justify-content: center;
          flex-direction: column;
          box-sizing: border-box;
        }
        a {
          color: var(--primary-color);
        }
        ha-alert {
          margin-bottom: 16px;
        }
      `))]}constructor(...o){super(...o),this.toolbar=!0,this.rootnav=!1,this.narrow=!1}}(0,e.__decorate)([(0,n.MZ)({attribute:!1})],f.prototype,"hass",void 0),(0,e.__decorate)([(0,n.MZ)({type:Boolean})],f.prototype,"toolbar",void 0),(0,e.__decorate)([(0,n.MZ)({type:Boolean})],f.prototype,"rootnav",void 0),(0,e.__decorate)([(0,n.MZ)({type:Boolean})],f.prototype,"narrow",void 0),(0,e.__decorate)([(0,n.MZ)()],f.prototype,"error",void 0),f=(0,e.__decorate)([(0,n.EM)("hass-error-screen")],f),r()}catch(d){r(d)}}))},89180:function(o,t,a){var r=a(6764),e=Math.floor,i=function(o,t){var a=o.length;if(a<8)for(var n,l,s=1;s<a;){for(l=s,n=o[s];l&&t(o[l-1],n)>0;)o[l]=o[--l];l!==s++&&(o[l]=n)}else for(var c=e(a/2),d=i(r(o,0,c),t),h=i(r(o,c),t),u=d.length,p=h.length,v=0,b=0;v<u||b<p;)o[v+b]=v<u&&b<p?t(d[v],h[b])<=0?d[v++]:h[b++]:v<u?d[v++]:h[b++];return o};o.exports=i},78609:function(o,t,a){var r=a(94971).match(/firefox\/(\d+)/i);o.exports=!!r&&+r[1]},69615:function(o,t,a){var r=a(94971);o.exports=/MSIE|Trident/.test(r)},33651:function(o,t,a){var r=a(94971).match(/AppleWebKit\/(\d+)\./);o.exports=!!r&&+r[1]},75513:function(o,t,a){var r=a(36196),e=a(50941);o.exports=function(o){if(e){try{return r.process.getBuiltinModule(o)}catch(t){}try{return Function('return require("'+o+'")')()}catch(t){}}}}}]);
//# sourceMappingURL=2583.fba29fc3d89c48ec.js.map