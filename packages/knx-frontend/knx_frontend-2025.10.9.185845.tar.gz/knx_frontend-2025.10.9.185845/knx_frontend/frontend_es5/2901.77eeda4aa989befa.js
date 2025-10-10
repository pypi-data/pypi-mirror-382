"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2901"],{86543:function(t,e,o){o.d(e,{v:function(){return i}});o(79827),o(35748),o(18223),o(95013);const i=(t,e,o,i)=>{const[a,n,r]=t.split(".",3);return Number(a)>e||Number(a)===e&&(void 0===i?Number(n)>=o:Number(n)>o)||void 0!==i&&Number(a)===e&&Number(n)===o&&Number(r)>=i}},3371:function(t,e,o){o.d(e,{d:function(){return i}});const i=t=>{switch(t.language){case"cs":case"de":case"fi":case"fr":case"sk":case"sv":return" ";default:return""}}},76943:function(t,e,o){o.a(t,(async function(t,e){try{o(35748),o(95013);var i=o(69868),a=o(60498),n=o(84922),r=o(11991),l=t([a]);a=(l.then?(await l)():l)[0];let d,s=t=>t;class c extends a.A{static get styles(){return[a.A.styles,(0,n.AH)(d||(d=s`
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
      `))]}constructor(...t){super(...t),this.variant="brand"}}c=(0,i.__decorate)([(0,r.EM)("ha-button")],c),e()}catch(d){e(d)}}))},81571:function(t,e,o){o.a(t,(async function(t,e){try{o(35748),o(65315),o(37089),o(95013);var i=o(69868),a=o(76440),n=o(84922),r=o(11991),l=o(75907),d=o(73120),s=o(76943),c=(o(93672),o(3371)),p=o(26846),h=o(88234),u=t([a,s]);[a,s]=u.then?(await u)():u;let f,v,g,x,m,b,_,y,k=t=>t;const w="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z",$="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M13.5,16V19H10.5V16H8L12,12L16,16H13.5M13,9V3.5L18.5,9H13Z";class j extends n.WF{firstUpdated(t){super.firstUpdated(t),this.autoOpenFileDialog&&this._openFilePicker()}get _name(){if(void 0===this.value)return"";if("string"==typeof this.value)return this.value;return(this.value instanceof FileList?Array.from(this.value):(0,p.e)(this.value)).map((t=>t.name)).join(", ")}render(){const t=this.localize||this.hass.localize;return(0,n.qy)(f||(f=k`
      ${0}
    `),this.uploading?(0,n.qy)(v||(v=k`<div class="container">
            <div class="uploading">
              <span class="header"
                >${0}</span
              >
              ${0}
            </div>
            <mwc-linear-progress
              .indeterminate=${0}
              .progress=${0}
            ></mwc-linear-progress>
          </div>`),this.uploadingLabel||(this.value?t("ui.components.file-upload.uploading_name",{name:this._name}):t("ui.components.file-upload.uploading")),this.progress?(0,n.qy)(g||(g=k`<div class="progress">
                    ${0}${0}%
                  </div>`),this.progress,this.hass&&(0,c.d)(this.hass.locale)):n.s6,!this.progress,this.progress?this.progress/100:void 0):(0,n.qy)(x||(x=k`<label
            for=${0}
            class="container ${0}"
            @drop=${0}
            @dragenter=${0}
            @dragover=${0}
            @dragleave=${0}
            @dragend=${0}
            >${0}
            <input
              id="input"
              type="file"
              class="file"
              .accept=${0}
              .multiple=${0}
              @change=${0}
          /></label>`),this.value?"":"input",(0,l.H)({dragged:this._drag,multiple:this.multiple,value:Boolean(this.value)}),this._handleDrop,this._handleDragStart,this._handleDragStart,this._handleDragEnd,this._handleDragEnd,this.value?"string"==typeof this.value?(0,n.qy)(b||(b=k`<div class="row">
                    <div class="value" @click=${0}>
                      <ha-svg-icon
                        .path=${0}
                      ></ha-svg-icon>
                      ${0}
                    </div>
                    <ha-icon-button
                      @click=${0}
                      .label=${0}
                      .path=${0}
                    ></ha-icon-button>
                  </div>`),this._openFilePicker,this.icon||$,this.value,this._clearValue,this.deleteLabel||t("ui.common.delete"),w):(this.value instanceof FileList?Array.from(this.value):(0,p.e)(this.value)).map((e=>(0,n.qy)(_||(_=k`<div class="row">
                        <div class="value" @click=${0}>
                          <ha-svg-icon
                            .path=${0}
                          ></ha-svg-icon>
                          ${0} - ${0}
                        </div>
                        <ha-icon-button
                          @click=${0}
                          .label=${0}
                          .path=${0}
                        ></ha-icon-button>
                      </div>`),this._openFilePicker,this.icon||$,e.name,(0,h.A)(e.size),this._clearValue,this.deleteLabel||t("ui.common.delete"),w))):(0,n.qy)(m||(m=k`<ha-button
                    size="small"
                    appearance="filled"
                    @click=${0}
                  >
                    <ha-svg-icon
                      slot="start"
                      .path=${0}
                    ></ha-svg-icon>
                    ${0}
                  </ha-button>
                  <span class="secondary"
                    >${0}</span
                  >
                  <span class="supports">${0}</span>`),this._openFilePicker,this.icon||$,this.label||t("ui.components.file-upload.label"),this.secondary||t("ui.components.file-upload.secondary"),this.supports),this.accept,this.multiple,this._handleFilePicked))}_openFilePicker(){var t;null===(t=this._input)||void 0===t||t.click()}_handleDrop(t){var e;t.preventDefault(),t.stopPropagation(),null!==(e=t.dataTransfer)&&void 0!==e&&e.files&&(0,d.r)(this,"file-picked",{files:this.multiple||1===t.dataTransfer.files.length?Array.from(t.dataTransfer.files):[t.dataTransfer.files[0]]}),this._drag=!1}_handleDragStart(t){t.preventDefault(),t.stopPropagation(),this._drag=!0}_handleDragEnd(t){t.preventDefault(),t.stopPropagation(),this._drag=!1}_handleFilePicked(t){0!==t.target.files.length&&(this.value=t.target.files,(0,d.r)(this,"file-picked",{files:t.target.files}))}_clearValue(t){t.preventDefault(),this._input.value="",this.value=void 0,(0,d.r)(this,"change"),(0,d.r)(this,"files-cleared")}constructor(...t){super(...t),this.multiple=!1,this.disabled=!1,this.uploading=!1,this.autoOpenFileDialog=!1,this._drag=!1}}j.styles=(0,n.AH)(y||(y=k`
    :host {
      display: block;
      height: 240px;
    }
    :host([disabled]) {
      pointer-events: none;
      color: var(--disabled-text-color);
    }
    .container {
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      border: solid 1px
        var(--mdc-text-field-idle-line-color, rgba(0, 0, 0, 0.42));
      border-radius: var(--mdc-shape-small, 4px);
      height: 100%;
    }
    .row {
      display: flex;
      align-items: center;
    }
    label.container {
      border: dashed 1px
        var(--mdc-text-field-idle-line-color, rgba(0, 0, 0, 0.42));
      cursor: pointer;
    }
    .container .uploading {
      display: flex;
      flex-direction: column;
      width: 100%;
      align-items: flex-start;
      padding: 0 32px;
      box-sizing: border-box;
    }
    :host([disabled]) .container {
      border-color: var(--disabled-color);
    }
    label:hover,
    label.dragged {
      border-style: solid;
    }
    label.dragged {
      border-color: var(--primary-color);
    }
    .dragged:before {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      background-color: var(--primary-color);
      content: "";
      opacity: var(--dark-divider-opacity);
      pointer-events: none;
      border-radius: var(--mdc-shape-small, 4px);
    }
    label.value {
      cursor: default;
    }
    label.value.multiple {
      justify-content: unset;
      overflow: auto;
    }
    .highlight {
      color: var(--primary-color);
    }
    ha-button {
      margin-bottom: 8px;
    }
    .supports {
      color: var(--secondary-text-color);
      font-size: var(--ha-font-size-s);
    }
    :host([disabled]) .secondary {
      color: var(--disabled-text-color);
    }
    input.file {
      display: none;
    }
    .value {
      cursor: pointer;
    }
    .value ha-svg-icon {
      margin-right: 8px;
      margin-inline-end: 8px;
      margin-inline-start: initial;
    }
    ha-button {
      --mdc-button-outline-color: var(--primary-color);
      --mdc-icon-button-size: 24px;
    }
    mwc-linear-progress {
      width: 100%;
      padding: 8px 32px;
      box-sizing: border-box;
    }
    .header {
      font-weight: var(--ha-font-weight-medium);
    }
    .progress {
      color: var(--secondary-text-color);
    }
    button.link {
      background: none;
      border: none;
      padding: 0;
      font-size: var(--ha-font-size-m);
      color: var(--primary-color);
      text-decoration: underline;
      cursor: pointer;
    }
  `)),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],j.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],j.prototype,"localize",void 0),(0,i.__decorate)([(0,r.MZ)()],j.prototype,"accept",void 0),(0,i.__decorate)([(0,r.MZ)()],j.prototype,"icon",void 0),(0,i.__decorate)([(0,r.MZ)()],j.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)()],j.prototype,"secondary",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"uploading-label"})],j.prototype,"uploadingLabel",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"delete-label"})],j.prototype,"deleteLabel",void 0),(0,i.__decorate)([(0,r.MZ)()],j.prototype,"supports",void 0),(0,i.__decorate)([(0,r.MZ)({type:Object})],j.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],j.prototype,"multiple",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],j.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],j.prototype,"uploading",void 0),(0,i.__decorate)([(0,r.MZ)({type:Number})],j.prototype,"progress",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,attribute:"auto-open-file-dialog"})],j.prototype,"autoOpenFileDialog",void 0),(0,i.__decorate)([(0,r.wk)()],j.prototype,"_drag",void 0),(0,i.__decorate)([(0,r.P)("#input")],j.prototype,"_input",void 0),j=(0,i.__decorate)([(0,r.EM)("ha-file-upload")],j),e()}catch(f){e(f)}}))},11934:function(t,e,o){o.d(e,{h:function(){return f}});o(35748),o(95013);var i=o(69868),a=o(98252),n=o(27705),r=o(84922),l=o(11991),d=o(90933);let s,c,p,h,u=t=>t;class f extends a.J{updated(t){super.updated(t),(t.has("invalid")||t.has("errorMessage"))&&(this.setCustomValidity(this.invalid?this.errorMessage||this.validationMessage||"Invalid":""),(this.invalid||this.validateOnInitialRender||t.has("invalid")&&void 0!==t.get("invalid"))&&this.reportValidity()),t.has("autocomplete")&&(this.autocomplete?this.formElement.setAttribute("autocomplete",this.autocomplete):this.formElement.removeAttribute("autocomplete")),t.has("autocorrect")&&(!1===this.autocorrect?this.formElement.setAttribute("autocorrect","off"):this.formElement.removeAttribute("autocorrect")),t.has("inputSpellcheck")&&(this.inputSpellcheck?this.formElement.setAttribute("spellcheck",this.inputSpellcheck):this.formElement.removeAttribute("spellcheck"))}renderIcon(t,e=!1){const o=e?"trailing":"leading";return(0,r.qy)(s||(s=u`
      <span
        class="mdc-text-field__icon mdc-text-field__icon--${0}"
        tabindex=${0}
      >
        <slot name="${0}Icon"></slot>
      </span>
    `),o,e?1:-1,o)}constructor(...t){super(...t),this.icon=!1,this.iconTrailing=!1,this.autocorrect=!0}}f.styles=[n.R,(0,r.AH)(c||(c=u`
      .mdc-text-field__input {
        width: var(--ha-textfield-input-width, 100%);
      }
      .mdc-text-field:not(.mdc-text-field--with-leading-icon) {
        padding: var(--text-field-padding, 0px 16px);
      }
      .mdc-text-field__affix--suffix {
        padding-left: var(--text-field-suffix-padding-left, 12px);
        padding-right: var(--text-field-suffix-padding-right, 0px);
        padding-inline-start: var(--text-field-suffix-padding-left, 12px);
        padding-inline-end: var(--text-field-suffix-padding-right, 0px);
        direction: ltr;
      }
      .mdc-text-field--with-leading-icon {
        padding-inline-start: var(--text-field-suffix-padding-left, 0px);
        padding-inline-end: var(--text-field-suffix-padding-right, 16px);
        direction: var(--direction);
      }

      .mdc-text-field--with-leading-icon.mdc-text-field--with-trailing-icon {
        padding-left: var(--text-field-suffix-padding-left, 0px);
        padding-right: var(--text-field-suffix-padding-right, 0px);
        padding-inline-start: var(--text-field-suffix-padding-left, 0px);
        padding-inline-end: var(--text-field-suffix-padding-right, 0px);
      }
      .mdc-text-field:not(.mdc-text-field--disabled)
        .mdc-text-field__affix--suffix {
        color: var(--secondary-text-color);
      }

      .mdc-text-field:not(.mdc-text-field--disabled) .mdc-text-field__icon {
        color: var(--secondary-text-color);
      }

      .mdc-text-field__icon--leading {
        margin-inline-start: 16px;
        margin-inline-end: 8px;
        direction: var(--direction);
      }

      .mdc-text-field__icon--trailing {
        padding: var(--textfield-icon-trailing-padding, 12px);
      }

      .mdc-floating-label:not(.mdc-floating-label--float-above) {
        max-width: calc(100% - 16px);
      }

      .mdc-floating-label--float-above {
        max-width: calc((100% - 16px) / 0.75);
        transition: none;
      }

      input {
        text-align: var(--text-field-text-align, start);
      }

      input[type="color"] {
        height: 20px;
      }

      /* Edge, hide reveal password icon */
      ::-ms-reveal {
        display: none;
      }

      /* Chrome, Safari, Edge, Opera */
      :host([no-spinner]) input::-webkit-outer-spin-button,
      :host([no-spinner]) input::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
      }

      input[type="color"]::-webkit-color-swatch-wrapper {
        padding: 0;
      }

      /* Firefox */
      :host([no-spinner]) input[type="number"] {
        -moz-appearance: textfield;
      }

      .mdc-text-field__ripple {
        overflow: hidden;
      }

      .mdc-text-field {
        overflow: var(--text-field-overflow);
      }

      .mdc-floating-label {
        padding-inline-end: 16px;
        padding-inline-start: initial;
        inset-inline-start: 16px !important;
        inset-inline-end: initial !important;
        transform-origin: var(--float-start);
        direction: var(--direction);
        text-align: var(--float-start);
        box-sizing: border-box;
        text-overflow: ellipsis;
      }

      .mdc-text-field--with-leading-icon.mdc-text-field--filled
        .mdc-floating-label {
        max-width: calc(
          100% - 48px - var(--text-field-suffix-padding-left, 0px)
        );
        inset-inline-start: calc(
          48px + var(--text-field-suffix-padding-left, 0px)
        ) !important;
        inset-inline-end: initial !important;
        direction: var(--direction);
      }

      .mdc-text-field__input[type="number"] {
        direction: var(--direction);
      }
      .mdc-text-field__affix--prefix {
        padding-right: var(--text-field-prefix-padding-right, 2px);
        padding-inline-end: var(--text-field-prefix-padding-right, 2px);
        padding-inline-start: initial;
      }

      .mdc-text-field:not(.mdc-text-field--disabled)
        .mdc-text-field__affix--prefix {
        color: var(--mdc-text-field-label-ink-color);
      }
      #helper-text ha-markdown {
        display: inline-block;
      }
    `)),"rtl"===d.G.document.dir?(0,r.AH)(p||(p=u`
          .mdc-text-field--with-leading-icon,
          .mdc-text-field__icon--leading,
          .mdc-floating-label,
          .mdc-text-field--with-leading-icon.mdc-text-field--filled
            .mdc-floating-label,
          .mdc-text-field__input[type="number"] {
            direction: rtl;
            --direction: rtl;
          }
        `)):(0,r.AH)(h||(h=u``))],(0,i.__decorate)([(0,l.MZ)({type:Boolean})],f.prototype,"invalid",void 0),(0,i.__decorate)([(0,l.MZ)({attribute:"error-message"})],f.prototype,"errorMessage",void 0),(0,i.__decorate)([(0,l.MZ)({type:Boolean})],f.prototype,"icon",void 0),(0,i.__decorate)([(0,l.MZ)({type:Boolean})],f.prototype,"iconTrailing",void 0),(0,i.__decorate)([(0,l.MZ)()],f.prototype,"autocomplete",void 0),(0,i.__decorate)([(0,l.MZ)({type:Boolean})],f.prototype,"autocorrect",void 0),(0,i.__decorate)([(0,l.MZ)({attribute:"input-spellcheck"})],f.prototype,"inputSpellcheck",void 0),(0,i.__decorate)([(0,l.P)("input")],f.prototype,"formElement",void 0),f=(0,i.__decorate)([(0,l.EM)("ha-textfield")],f)},40679:function(t,e,o){o.d(e,{Q:function(){return i},n:function(){return a}});o(46852),o(5934);const i=async(t,e)=>{const o=new FormData;o.append("file",e);const i=await t.fetchWithAuth("/api/file_upload",{method:"POST",body:o});if(413===i.status)throw new Error(`Uploaded file is too large (${e.name})`);if(200!==i.status)throw new Error("Unknown error");return(await i.json()).file_id},a=async(t,e)=>t.callApi("DELETE","file_upload",{file_id:e})},38:function(t,e,o){o.d(e,{PS:function(){return i},VR:function(){return a}});o(79827),o(35748),o(5934),o(88238),o(34536),o(16257),o(20152),o(44711),o(72108),o(77030),o(18223),o(95013),o(86543);const i=t=>t.data,a=t=>"object"==typeof t?"object"==typeof t.body?t.body.message||"Unknown error, see supervisor logs":t.body||t.message||"Unknown error, see supervisor logs":t;new Set([502,503,504])},47420:function(t,e,o){o.d(e,{K$:function(){return r},an:function(){return d},dk:function(){return l}});o(35748),o(12977),o(5934),o(95013);var i=o(73120);const a=()=>Promise.all([o.e("6143"),o.e("9543"),o.e("915")]).then(o.bind(o,30478)),n=(t,e,o)=>new Promise((n=>{const r=e.cancel,l=e.confirm;(0,i.r)(t,"show-dialog",{dialogTag:"dialog-box",dialogImport:a,dialogParams:Object.assign(Object.assign(Object.assign({},e),o),{},{cancel:()=>{n(!(null==o||!o.prompt)&&null),r&&r()},confirm:t=>{n(null==o||!o.prompt||t),l&&l(t)}})})})),r=(t,e)=>n(t,e),l=(t,e)=>n(t,e,{confirmation:!0}),d=(t,e)=>n(t,e,{prompt:!0})},30808:function(t,e,o){o.a(t,(async function(t,e){try{o(35748),o(5934),o(95013);var i=o(30808),a=t([i]);i=(a.then?(await a)():a)[0],"function"!=typeof window.ResizeObserver&&(window.ResizeObserver=(await o.e("997").then(o.bind(o,948))).default),e()}catch(n){e(n)}}),1)},88234:function(t,e,o){o.d(e,{A:function(){return i}});o(92344),o(91455);const i=(t=0,e=2)=>{if(0===t)return"0 Bytes";e=e<0?0:e;const o=Math.floor(Math.log(t)/Math.log(1024));return`${parseFloat((t/1024**o).toFixed(e))} ${["Bytes","KB","MB","GB","TB","PB","EB","ZB","YB"][o]}`}},25525:function(t,e,o){o.d(e,{x:function(){return i}});const i="2025.10.9.185845"},61118:function(t,e,o){o.a(t,(async function(t,i){try{o.r(e),o.d(e,{KNXInfo:function(){return M}});o(35748),o(5934),o(95013);var a=o(69868),n=o(84922),r=o(11991),l=o(73120),d=(o(86853),o(54885),o(76943)),s=o(81571),c=o(18664),p=o(40679),h=o(38),u=o(47420),f=o(49432),v=o(92095),g=o(25525),x=t([d,s,c]);[d,s,c]=x.then?(await x)():x;let m,b,_,y,k,w=t=>t;const $="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M13.5,16V19H10.5V16H8L12,12L16,16H13.5M13,9V3.5L18.5,9H13Z",j=new v.Q("info");class M extends n.WF{render(){return(0,n.qy)(m||(m=w`
      <hass-tabs-subpage
        .hass=${0}
        .narrow=${0}
        .route=${0}
        .tabs=${0}
        .localizeFunc=${0}
      >
        <div class="columns">
          ${0}
          ${0}
          ${0}
        </div>
      </hass-tabs-subpage>
    `),this.hass,this.narrow,this.route,this.tabs,this.knx.localize,this._renderInfoCard(),this.knx.projectInfo?this._renderProjectDataCard(this.knx.projectInfo):n.s6,this._renderProjectUploadCard())}_renderInfoCard(){return(0,n.qy)(b||(b=w` <ha-card class="knx-info">
      <div class="card-content knx-info-section">
        <div class="knx-content-row header">${0}</div>

        <div class="knx-content-row">
          <div>XKNX Version</div>
          <div>${0}</div>
        </div>

        <div class="knx-content-row">
          <div>KNX-Frontend Version</div>
          <div>${0}</div>
        </div>

        <div class="knx-content-row">
          <div>${0}</div>
          <div>
            ${0}
          </div>
        </div>

        <div class="knx-content-row">
          <div>${0}</div>
          <div>${0}</div>
        </div>

        <div class="knx-bug-report">
          ${0}
          <a href="https://github.com/XKNX/knx-integration" target="_blank">xknx/knx-integration</a>
        </div>

        <div class="knx-bug-report">
          ${0}
          <a href="https://my.knx.org" target="_blank">my.knx.org</a>
        </div>
      </div>
    </ha-card>`),this.knx.localize("info_information_header"),this.knx.connectionInfo.version,g.x,this.knx.localize("info_connected_to_bus"),this.hass.localize(this.knx.connectionInfo.connected?"ui.common.yes":"ui.common.no"),this.knx.localize("info_individual_address"),this.knx.connectionInfo.current_address,this.knx.localize("info_issue_tracker"),this.knx.localize("info_my_knx"))}_renderProjectDataCard(t){return(0,n.qy)(_||(_=w`
      <ha-card class="knx-info">
          <div class="card-content knx-content">
            <div class="header knx-content-row">
              ${0}
            </div>
            <div class="knx-content-row">
              <div>${0}</div>
              <div>${0}</div>
            </div>
            <div class="knx-content-row">
              <div>${0}</div>
              <div>${0}</div>
            </div>
            <div class="knx-content-row">
              <div>${0}</div>
              <div>${0}</div>
            </div>
            <div class="knx-content-row">
              <div>${0}</div>
              <div>${0}</div>
            </div>
            <div class="knx-button-row">
              <ha-button
                class="knx-warning push-right"
                @click=${0}
                .disabled=${0}
                >
                ${0}
              </ha-button>
            </div>
          </div>
        </div>
      </ha-card>
    `),this.knx.localize("info_project_data_header"),this.knx.localize("info_project_data_name"),t.name,this.knx.localize("info_project_data_last_modified"),new Date(t.last_modified).toUTCString(),this.knx.localize("info_project_data_tool_version"),t.tool_version,this.knx.localize("info_project_data_xknxproject_version"),t.xknxproject_version,this._removeProject,this._uploading||!this.knx.projectInfo,this.knx.localize("info_project_delete"))}_renderProjectUploadCard(){var t;return(0,n.qy)(y||(y=w` <ha-card class="knx-info">
      <div class="card-content knx-content">
        <div class="knx-content-row header">${0}</div>
        <div class="knx-content-row">${0}</div>
        <div class="knx-content-row">
          <ha-file-upload
            .hass=${0}
            accept=".knxproj, .knxprojarchive"
            .icon=${0}
            .label=${0}
            .value=${0}
            .uploading=${0}
            @file-picked=${0}
          ></ha-file-upload>
        </div>
        <div class="knx-content-row">
          <ha-selector-text
            .hass=${0}
            .value=${0}
            .label=${0}
            .selector=${0}
            .required=${0}
            @value-changed=${0}
          >
          </ha-selector-text>
        </div>
        <div class="knx-button-row">
          <ha-button
            class="push-right"
            @click=${0}
            .disabled=${0}
            >${0}</ha-button
          >
        </div>
      </div>
    </ha-card>`),this.knx.localize("info_project_file_header"),this.knx.localize("info_project_upload_description"),this.hass,$,this.knx.localize("info_project_file"),null===(t=this._projectFile)||void 0===t?void 0:t.name,this._uploading,this._filePicked,this.hass,this._projectPassword||"",this.hass.localize("ui.login-form.password"),{text:{multiline:!1,type:"password"}},!1,this._passwordChanged,this._uploadFile,this._uploading||!this._projectFile,this.hass.localize("ui.common.submit"))}_filePicked(t){this._projectFile=t.detail.files[0]}_passwordChanged(t){this._projectPassword=t.detail.value}async _uploadFile(t){const e=this._projectFile;if(void 0===e)return;let o;this._uploading=!0;try{const t=await(0,p.Q)(this.hass,e);await(0,f.dc)(this.hass,t,this._projectPassword||"")}catch(i){o=i,(0,u.K$)(this,{title:"Upload failed",text:(0,h.VR)(i)})}finally{o||(this._projectFile=void 0,this._projectPassword=void 0),this._uploading=!1,(0,l.r)(this,"knx-reload")}}async _removeProject(t){if(await(0,u.dk)(this,{text:this.knx.localize("info_project_delete")}))try{await(0,f.gV)(this.hass)}catch(e){(0,u.K$)(this,{title:"Deletion failed",text:(0,h.VR)(e)})}finally{(0,l.r)(this,"knx-reload")}else j.debug("User cancelled deletion")}constructor(...t){super(...t),this._uploading=!1}}M.styles=(0,n.AH)(k||(k=w`
    .columns {
      display: flex;
      justify-content: center;
    }

    @media screen and (max-width: 1232px) {
      .columns {
        flex-direction: column;
      }

      .knx-button-row {
        margin-top: 20px;
      }

      .knx-info {
        margin-right: 8px;
      }
    }

    @media screen and (min-width: 1233px) {
      .knx-button-row {
        margin-top: auto;
      }

      .knx-info {
        width: 400px;
      }
    }

    .knx-info {
      margin-left: 8px;
      margin-top: 8px;
    }

    .knx-content {
      display: flex;
      flex-direction: column;
      height: 100%;
      box-sizing: border-box;
    }

    .knx-content-row {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
    }

    .knx-content-row > div:nth-child(2) {
      margin-left: 1rem;
    }

    .knx-button-row {
      display: flex;
      flex-direction: row;
      vertical-align: bottom;
      padding-top: 16px;
    }

    .push-left {
      margin-right: auto;
    }

    .push-right {
      margin-left: auto;
    }

    .knx-warning {
      --mdc-theme-primary: var(--error-color);
    }

    .knx-project-description {
      margin-top: -8px;
      padding: 0px 16px 16px;
    }

    .knx-delete-project-button {
      position: absolute;
      bottom: 0;
      right: 0;
    }

    .knx-bug-report {
      margin-top: 20px;

      a {
        text-decoration: none;
      }
    }

    .header {
      color: var(--ha-card-header-color, --primary-text-color);
      font-family: var(--ha-card-header-font-family, inherit);
      font-size: var(--ha-card-header-font-size, 24px);
      letter-spacing: -0.012em;
      line-height: 48px;
      padding: -4px 16px 16px;
      display: inline-block;
      margin-block-start: 0px;
      margin-block-end: 4px;
      font-weight: normal;
    }

    ha-file-upload,
    ha-selector-text {
      width: 100%;
      margin-top: 8px;
    }
  `)),(0,a.__decorate)([(0,r.MZ)({type:Object})],M.prototype,"hass",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],M.prototype,"knx",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],M.prototype,"narrow",void 0),(0,a.__decorate)([(0,r.MZ)({type:Object})],M.prototype,"route",void 0),(0,a.__decorate)([(0,r.MZ)({type:Array,reflect:!1})],M.prototype,"tabs",void 0),(0,a.__decorate)([(0,r.wk)()],M.prototype,"_projectPassword",void 0),(0,a.__decorate)([(0,r.wk)()],M.prototype,"_uploading",void 0),(0,a.__decorate)([(0,r.wk)()],M.prototype,"_projectFile",void 0),M=(0,a.__decorate)([(0,r.EM)("knx-info")],M),i()}catch(m){i(m)}}))}}]);
//# sourceMappingURL=2901.77eeda4aa989befa.js.map