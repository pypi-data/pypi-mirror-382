export const __webpack_id__="9502";export const __webpack_ids__=["9502"];export const __webpack_modules__={23749:function(t,o,e){e.r(o);var i=e(69868),a=e(84922),r=e(11991),n=e(75907),l=e(73120);e(93672),e(95635);const s={info:"M11,9H13V7H11M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,17H13V11H11V17Z",warning:"M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16",error:"M11,15H13V17H11V15M11,7H13V13H11V7M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20Z",success:"M20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4C12.76,4 13.5,4.11 14.2,4.31L15.77,2.74C14.61,2.26 13.34,2 12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12M7.91,10.08L6.5,11.5L11,16L21,6L19.59,4.58L11,13.17L7.91,10.08Z"};class d extends a.WF{render(){return a.qy`
      <div
        class="issue-type ${(0,n.H)({[this.alertType]:!0})}"
        role="alert"
      >
        <div class="icon ${this.title?"":"no-title"}">
          <slot name="icon">
            <ha-svg-icon .path=${s[this.alertType]}></ha-svg-icon>
          </slot>
        </div>
        <div class=${(0,n.H)({content:!0,narrow:this.narrow})}>
          <div class="main-content">
            ${this.title?a.qy`<div class="title">${this.title}</div>`:a.s6}
            <slot></slot>
          </div>
          <div class="action">
            <slot name="action">
              ${this.dismissable?a.qy`<ha-icon-button
                    @click=${this._dismissClicked}
                    label="Dismiss alert"
                    .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
                  ></ha-icon-button>`:a.s6}
            </slot>
          </div>
        </div>
      </div>
    `}_dismissClicked(){(0,l.r)(this,"alert-dismissed-clicked")}constructor(...t){super(...t),this.title="",this.alertType="info",this.dismissable=!1,this.narrow=!1}}d.styles=a.AH`
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
  `,(0,i.__decorate)([(0,r.MZ)()],d.prototype,"title",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"alert-type"})],d.prototype,"alertType",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],d.prototype,"dismissable",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],d.prototype,"narrow",void 0),d=(0,i.__decorate)([(0,r.EM)("ha-alert")],d)},76943:function(t,o,e){e.a(t,(async function(t,o){try{var i=e(69868),a=e(60498),r=e(84922),n=e(11991),l=t([a]);a=(l.then?(await l)():l)[0];class s extends a.A{static get styles(){return[a.A.styles,r.AH`
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
      `]}constructor(...t){super(...t),this.variant="brand"}}s=(0,i.__decorate)([(0,n.EM)("ha-button")],s),o()}catch(s){o(s)}}))},99741:function(t,o,e){e.d(o,{p:()=>d});var i=e(69868),a=e(84922),r=e(11991),n=e(75907),l=e(73120),s=e(93360);e(95635);class d extends a.WF{render(){const t=this.noCollapse?a.s6:a.qy`
          <ha-svg-icon
            .path=${"M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z"}
            class="summary-icon ${(0,n.H)({expanded:this.expanded})}"
          ></ha-svg-icon>
        `;return a.qy`
      <div class="top ${(0,n.H)({expanded:this.expanded})}">
        <div
          id="summary"
          class=${(0,n.H)({noCollapse:this.noCollapse})}
          @click=${this._toggleContainer}
          @keydown=${this._toggleContainer}
          @focus=${this._focusChanged}
          @blur=${this._focusChanged}
          role="button"
          tabindex=${this.noCollapse?-1:0}
          aria-expanded=${this.expanded}
          aria-controls="sect1"
        >
          ${this.leftChevron?t:a.s6}
          <slot name="leading-icon"></slot>
          <slot name="header">
            <div class="header">
              ${this.header}
              <slot class="secondary" name="secondary">${this.secondary}</slot>
            </div>
          </slot>
          ${this.leftChevron?a.s6:t}
          <slot name="icons"></slot>
        </div>
      </div>
      <div
        class="container ${(0,n.H)({expanded:this.expanded})}"
        @transitionend=${this._handleTransitionEnd}
        role="region"
        aria-labelledby="summary"
        aria-hidden=${!this.expanded}
        tabindex="-1"
      >
        ${this._showContent?a.qy`<slot></slot>`:""}
      </div>
    `}willUpdate(t){super.willUpdate(t),t.has("expanded")&&(this._showContent=this.expanded,setTimeout((()=>{this._container.style.overflow=this.expanded?"initial":"hidden"}),300))}_handleTransitionEnd(){this._container.style.removeProperty("height"),this._container.style.overflow=this.expanded?"initial":"hidden",this._showContent=this.expanded}async _toggleContainer(t){if(t.defaultPrevented)return;if("keydown"===t.type&&"Enter"!==t.key&&" "!==t.key)return;if(t.preventDefault(),this.noCollapse)return;const o=!this.expanded;(0,l.r)(this,"expanded-will-change",{expanded:o}),this._container.style.overflow="hidden",o&&(this._showContent=!0,await(0,s.E)());const e=this._container.scrollHeight;this._container.style.height=`${e}px`,o||setTimeout((()=>{this._container.style.height="0px"}),0),this.expanded=o,(0,l.r)(this,"expanded-changed",{expanded:this.expanded})}_focusChanged(t){this.noCollapse||this.shadowRoot.querySelector(".top").classList.toggle("focused","focus"===t.type)}constructor(...t){super(...t),this.expanded=!1,this.outlined=!1,this.leftChevron=!1,this.noCollapse=!1,this._showContent=this.expanded}}d.styles=a.AH`
    :host {
      display: block;
    }

    .top {
      display: flex;
      align-items: center;
      border-radius: var(--ha-card-border-radius, 12px);
    }

    .top.expanded {
      border-bottom-left-radius: 0px;
      border-bottom-right-radius: 0px;
    }

    .top.focused {
      background: var(--input-fill-color);
    }

    :host([outlined]) {
      box-shadow: none;
      border-width: 1px;
      border-style: solid;
      border-color: var(--outline-color);
      border-radius: var(--ha-card-border-radius, 12px);
    }

    .summary-icon {
      transition: transform 150ms cubic-bezier(0.4, 0, 0.2, 1);
      direction: var(--direction);
      margin-left: 8px;
      margin-inline-start: 8px;
      margin-inline-end: initial;
    }

    :host([left-chevron]) .summary-icon,
    ::slotted([slot="leading-icon"]) {
      margin-left: 0;
      margin-right: 8px;
      margin-inline-start: 0;
      margin-inline-end: 8px;
    }

    #summary {
      flex: 1;
      display: flex;
      padding: var(--expansion-panel-summary-padding, 0 8px);
      min-height: 48px;
      align-items: center;
      cursor: pointer;
      overflow: hidden;
      font-weight: var(--ha-font-weight-medium);
      outline: none;
    }
    #summary.noCollapse {
      cursor: default;
    }

    .summary-icon.expanded {
      transform: rotate(180deg);
    }

    .header,
    ::slotted([slot="header"]) {
      flex: 1;
      overflow-wrap: anywhere;
    }

    .container {
      padding: var(--expansion-panel-content-padding, 0 8px);
      overflow: hidden;
      transition: height 300ms cubic-bezier(0.4, 0, 0.2, 1);
      height: 0px;
    }

    .container.expanded {
      height: auto;
    }

    .secondary {
      display: block;
      color: var(--secondary-text-color);
      font-size: var(--ha-font-size-s);
    }
  `,(0,i.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],d.prototype,"expanded",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],d.prototype,"outlined",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"left-chevron",type:Boolean,reflect:!0})],d.prototype,"leftChevron",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"no-collapse",type:Boolean,reflect:!0})],d.prototype,"noCollapse",void 0),(0,i.__decorate)([(0,r.MZ)()],d.prototype,"header",void 0),(0,i.__decorate)([(0,r.MZ)()],d.prototype,"secondary",void 0),(0,i.__decorate)([(0,r.wk)()],d.prototype,"_showContent",void 0),(0,i.__decorate)([(0,r.P)(".container")],d.prototype,"_container",void 0),d=(0,i.__decorate)([(0,r.EM)("ha-expansion-panel")],d)},25223:function(t,o,e){var i=e(69868),a=e(41188),r=e(57437),n=e(84922),l=e(11991);class s extends a.J{renderRipple(){return this.noninteractive?"":super.renderRipple()}static get styles(){return[r.R,n.AH`
        :host {
          padding-left: var(
            --mdc-list-side-padding-left,
            var(--mdc-list-side-padding, 20px)
          );
          padding-inline-start: var(
            --mdc-list-side-padding-left,
            var(--mdc-list-side-padding, 20px)
          );
          padding-right: var(
            --mdc-list-side-padding-right,
            var(--mdc-list-side-padding, 20px)
          );
          padding-inline-end: var(
            --mdc-list-side-padding-right,
            var(--mdc-list-side-padding, 20px)
          );
        }
        :host([graphic="avatar"]:not([twoLine])),
        :host([graphic="icon"]:not([twoLine])) {
          height: 48px;
        }
        span.material-icons:first-of-type {
          margin-inline-start: 0px !important;
          margin-inline-end: var(
            --mdc-list-item-graphic-margin,
            16px
          ) !important;
          direction: var(--direction) !important;
        }
        span.material-icons:last-of-type {
          margin-inline-start: auto !important;
          margin-inline-end: 0px !important;
          direction: var(--direction) !important;
        }
        .mdc-deprecated-list-item__meta {
          display: var(--mdc-list-item-meta-display);
          align-items: center;
          flex-shrink: 0;
        }
        :host([graphic="icon"]:not([twoline]))
          .mdc-deprecated-list-item__graphic {
          margin-inline-end: var(
            --mdc-list-item-graphic-margin,
            20px
          ) !important;
        }
        :host([multiline-secondary]) {
          height: auto;
        }
        :host([multiline-secondary]) .mdc-deprecated-list-item__text {
          padding: 8px 0;
        }
        :host([multiline-secondary]) .mdc-deprecated-list-item__secondary-text {
          text-overflow: initial;
          white-space: normal;
          overflow: auto;
          display: inline-block;
          margin-top: 10px;
        }
        :host([multiline-secondary]) .mdc-deprecated-list-item__primary-text {
          margin-top: 10px;
        }
        :host([multiline-secondary])
          .mdc-deprecated-list-item__secondary-text::before {
          display: none;
        }
        :host([multiline-secondary])
          .mdc-deprecated-list-item__primary-text::before {
          display: none;
        }
        :host([disabled]) {
          color: var(--disabled-text-color);
        }
        :host([noninteractive]) {
          pointer-events: unset;
        }
      `,"rtl"===document.dir?n.AH`
            span.material-icons:first-of-type,
            span.material-icons:last-of-type {
              direction: rtl !important;
              --direction: rtl;
            }
          `:n.AH``]}}s=(0,i.__decorate)([(0,l.EM)("ha-list-item")],s)},19307:function(t,o,e){var i=e(69868),a=e(81484),r=e(60311),n=e(11991);class l extends a.iY{}l.styles=r.R,l=(0,i.__decorate)([(0,n.EM)("ha-list")],l)},95968:function(t,o,e){var i=e(69868),a=e(95463),r=e(3941),n=e(84922),l=e(11991),s=e(75907);e(19307);class d extends a.ZR{get listElement(){return this.listElement_||(this.listElement_=this.renderRoot.querySelector("ha-list")),this.listElement_}renderList(){const t="menu"===this.innerRole?"menuitem":"option",o=this.renderListClasses();return n.qy`<ha-list
      rootTabbable
      .innerAriaLabel=${this.innerAriaLabel}
      .innerRole=${this.innerRole}
      .multi=${this.multi}
      class=${(0,s.H)(o)}
      .itemRoles=${t}
      .wrapFocus=${this.wrapFocus}
      .activatable=${this.activatable}
      @action=${this.onAction}
    >
      <slot></slot>
    </ha-list>`}}d.styles=r.R,d=(0,i.__decorate)([(0,l.EM)("ha-menu")],d)},43143:function(t,o,e){var i=e(69868),a=e(7483),r=e(60055),n=e(84922),l=e(11991),s=e(30209);class d extends a.U{firstUpdated(){super.firstUpdated(),this.addEventListener("change",(()=>{this.haptic&&(0,s.j)("light")}))}constructor(...t){super(...t),this.haptic=!1}}d.styles=[r.R,n.AH`
      :host {
        --mdc-theme-secondary: var(--switch-checked-color);
      }
      .mdc-switch.mdc-switch--checked .mdc-switch__thumb {
        background-color: var(--switch-checked-button-color);
        border-color: var(--switch-checked-button-color);
      }
      .mdc-switch.mdc-switch--checked .mdc-switch__track {
        background-color: var(--switch-checked-track-color);
        border-color: var(--switch-checked-track-color);
      }
      .mdc-switch:not(.mdc-switch--checked) .mdc-switch__thumb {
        background-color: var(--switch-unchecked-button-color);
        border-color: var(--switch-unchecked-button-color);
      }
      .mdc-switch:not(.mdc-switch--checked) .mdc-switch__track {
        background-color: var(--switch-unchecked-track-color);
        border-color: var(--switch-unchecked-track-color);
      }
    `],(0,i.__decorate)([(0,l.MZ)({type:Boolean})],d.prototype,"haptic",void 0),d=(0,i.__decorate)([(0,l.EM)("ha-switch")],d)},30209:function(t,o,e){e.d(o,{j:()=>a});var i=e(73120);const a=t=>{(0,i.r)(window,"haptic",t)}},93060:function(t,o,e){e.d(o,{CY:()=>s,HF:()=>l,RL:()=>g,Vt:()=>r,Zc:()=>n,e4:()=>a,u_:()=>v});var i=e(90227);const a={payload:t=>null==t.payload?"":Array.isArray(t.payload)?t.payload.reduce(((t,o)=>t+o.toString(16).padStart(2,"0")),"0x"):t.payload.toString(),valueWithUnit:t=>null==t.value?"":"number"==typeof t.value||"boolean"==typeof t.value||"string"==typeof t.value?t.value.toString()+(t.unit?" "+t.unit:""):(0,i.Bh)(t.value),timeWithMilliseconds:t=>new Date(t.timestamp).toLocaleTimeString(["en-US"],{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),dateWithMilliseconds:t=>new Date(t.timestamp).toLocaleTimeString([],{year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),dptNumber:t=>null==t.dpt_main?"":null==t.dpt_sub?t.dpt_main.toString():t.dpt_main.toString()+"."+t.dpt_sub.toString().padStart(3,"0"),dptNameNumber:t=>{const o=a.dptNumber(t);return null==t.dpt_name?`DPT ${o}`:o?`DPT ${o} ${t.dpt_name}`:t.dpt_name}},r=t=>null==t?"":t.main+(t.sub?"."+t.sub.toString().padStart(3,"0"):""),n=t=>t.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),l=t=>t.toLocaleDateString(void 0,{year:"numeric",month:"2-digit",day:"2-digit"})+", "+t.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),s=t=>{const o=new Date(t),e=t.match(/\.(\d{6})/),i=e?e[1]:"000000";return o.toLocaleDateString(void 0,{year:"numeric",month:"2-digit",day:"2-digit"})+", "+o.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit"})+"."+i},d=1e3,c=1e3,h=60*c,p=60*h,u=2,m=3;function v(t){const o=t.indexOf(".");if(-1===o)return 1e3*Date.parse(t);let e=t.indexOf("Z",o);-1===e&&(e=t.indexOf("+",o),-1===e&&(e=t.indexOf("-",o))),-1===e&&(e=t.length);const i=t.slice(0,o)+t.slice(e),a=Date.parse(i);let r=t.slice(o+1,e);return r.length<6?r=r.padEnd(6,"0"):r.length>6&&(r=r.slice(0,6)),1e3*a+Number(r)}function g(t,o="milliseconds"){if(null==t)return"—";const e=t<0?"-":"",i=Math.abs(t),a="milliseconds"===o?Math.round(i/d):Math.floor(i/d),r="microseconds"===o?i%d:0,n=Math.floor(a/p),l=Math.floor(a%p/h),s=Math.floor(a%h/c),v=a%c,g=t=>t.toString().padStart(u,"0"),f=t=>t.toString().padStart(m,"0"),b="microseconds"===o?`.${f(v)}${f(r)}`:`.${f(v)}`,y=`${g(l)}:${g(s)}`;return`${e}${n>0?`${g(n)}:${y}`:y}${b}`}}};
//# sourceMappingURL=9502.cc4c81db54e05a37.js.map