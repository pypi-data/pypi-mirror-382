"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["5857"],{3371:function(e,t,i){i.d(t,{d:function(){return o}});const o=e=>{switch(e.language){case"cs":case"de":case"fi":case"fr":case"sk":case"sv":return" ";default:return""}}},18390:function(e,t,i){i.d(t,{A:function(){return r}});var o=i(3371);const r=(e,t)=>"°"===e?"":t&&"%"===e?(0,o.d)(t):" "},55266:function(e,t,i){i.d(t,{b:function(){return o}});i(35748),i(42124),i(86581),i(67579),i(39227),i(47849),i(88238),i(34536),i(16257),i(20152),i(44711),i(72108),i(77030),i(95013);const o=(e,t)=>{if(e===t)return!0;if(e&&t&&"object"==typeof e&&"object"==typeof t){if(e.constructor!==t.constructor)return!1;let i,r;if(Array.isArray(e)){if(r=e.length,r!==t.length)return!1;for(i=r;0!=i--;)if(!o(e[i],t[i]))return!1;return!0}if(e instanceof Map&&t instanceof Map){if(e.size!==t.size)return!1;for(i of e.entries())if(!t.has(i[0]))return!1;for(i of e.entries())if(!o(i[1],t.get(i[0])))return!1;return!0}if(e instanceof Set&&t instanceof Set){if(e.size!==t.size)return!1;for(i of e.entries())if(!t.has(i[0]))return!1;return!0}if(ArrayBuffer.isView(e)&&ArrayBuffer.isView(t)){if(r=e.length,r!==t.length)return!1;for(i=r;0!=i--;)if(e[i]!==t[i])return!1;return!0}if(e.constructor===RegExp)return e.source===t.source&&e.flags===t.flags;if(e.valueOf!==Object.prototype.valueOf)return e.valueOf()===t.valueOf();if(e.toString!==Object.prototype.toString)return e.toString()===t.toString();const a=Object.keys(e);if(r=a.length,r!==Object.keys(t).length)return!1;for(i=r;0!=i--;)if(!Object.prototype.hasOwnProperty.call(t,a[i]))return!1;for(i=r;0!=i--;){const r=a[i];if(!o(e[r],t[r]))return!1}return!0}return e!=e&&t!=t}},41480:function(e,t,i){i.a(e,(async function(e,o){try{i.r(t),i.d(t,{HaObjectSelector:function(){return k}});i(35748),i(99342),i(65315),i(37089),i(5934),i(95013);var r=i(69868),a=i(84922),s=i(11991),l=i(65940),n=i(26846),c=i(73120),d=i(66100),h=i(33728),u=(i(20014),i(5803),i(98343),i(8115),i(79080)),p=i(55266),m=e([u]);u=(m.then?(await m)():m)[0];let v,f,y,b,_,g,$,M,V,x,j,w,H=e=>e;const q="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",L="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z",Z="M7,19V17H9V19H7M11,19V17H13V19H11M15,19V17H17V19H15M7,15V13H9V15H7M11,15V13H13V15H11M15,15V13H17V15H15M7,11V9H9V11H7M11,11V9H13V11H11M15,11V9H17V11H15M7,7V5H9V7H7M11,7V5H13V7H11M15,7V5H17V7H15Z",O="M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z";class k extends a.WF{_renderItem(e,t){const i=this.selector.object.label_field||Object.keys(this.selector.object.fields)[0],o=this.selector.object.fields[i].selector,r=o?(0,d.C)(this.hass,e[i],o):"";let s="";const l=this.selector.object.description_field;if(l){const t=this.selector.object.fields[l].selector;s=t?(0,d.C)(this.hass,e[l],t):""}const n=this.selector.object.multiple||!1,c=this.selector.object.multiple||!1;return(0,a.qy)(v||(v=H`
      <ha-md-list-item class="item">
        ${0}
        <div slot="headline" class="label">${0}</div>
        ${0}
        <ha-icon-button
          slot="end"
          .item=${0}
          .index=${0}
          .label=${0}
          .path=${0}
          @click=${0}
        ></ha-icon-button>
        <ha-icon-button
          slot="end"
          .index=${0}
          .label=${0}
          .path=${0}
          @click=${0}
        ></ha-icon-button>
      </ha-md-list-item>
    `),n?(0,a.qy)(f||(f=H`
              <ha-svg-icon
                class="handle"
                .path=${0}
                slot="start"
              ></ha-svg-icon>
            `),Z):a.s6,r,s?(0,a.qy)(y||(y=H`<div slot="supporting-text" class="description">
              ${0}
            </div>`),s):a.s6,e,t,this.hass.localize("ui.common.edit"),O,this._editItem,t,this.hass.localize("ui.common.delete"),c?L:q,this._deleteItem)}render(){var e;if(null!==(e=this.selector.object)&&void 0!==e&&e.fields){if(this.selector.object.multiple){var t;const e=(0,n.e)(null!==(t=this.value)&&void 0!==t?t:[]);return(0,a.qy)(b||(b=H`
          ${0}
          <div class="items-container">
            <ha-sortable
              handle-selector=".handle"
              draggable-selector=".item"
              @item-moved=${0}
            >
              <ha-md-list>
                ${0}
              </ha-md-list>
            </ha-sortable>
            <ha-button appearance="filled" @click=${0}>
              ${0}
            </ha-button>
          </div>
        `),this.label?(0,a.qy)(_||(_=H`<label>${0}</label>`),this.label):a.s6,this._itemMoved,e.map(((e,t)=>this._renderItem(e,t))),this._addItem,this.hass.localize("ui.common.add"))}return(0,a.qy)(g||(g=H`
        ${0}
        <div class="items-container">
          ${0}
        </div>
      `),this.label?(0,a.qy)($||($=H`<label>${0}</label>`),this.label):a.s6,this.value?(0,a.qy)(M||(M=H`<ha-md-list>
                ${0}
              </ha-md-list>`),this._renderItem(this.value,0)):(0,a.qy)(V||(V=H`
                <ha-button appearance="filled" @click=${0}>
                  ${0}
                </ha-button>
              `),this._addItem,this.hass.localize("ui.common.add")))}return(0,a.qy)(x||(x=H`<ha-yaml-editor
        .hass=${0}
        .readonly=${0}
        .label=${0}
        .required=${0}
        .placeholder=${0}
        .defaultValue=${0}
        @value-changed=${0}
      ></ha-yaml-editor>
      ${0} `),this.hass,this.disabled,this.label,this.required,this.placeholder,this.value,this._handleChange,this.helper?(0,a.qy)(j||(j=H`<ha-input-helper-text .disabled=${0}
            >${0}</ha-input-helper-text
          >`),this.disabled,this.helper):"")}_itemMoved(e){var t;e.stopPropagation();const i=e.detail.newIndex,o=e.detail.oldIndex;if(!this.selector.object.multiple)return;const r=(0,n.e)(null!==(t=this.value)&&void 0!==t?t:[]).concat(),a=r.splice(o,1)[0];r.splice(i,0,a),(0,c.r)(this,"value-changed",{value:r})}async _addItem(e){var t;e.stopPropagation();const i=await(0,h.O)(this,{title:this.hass.localize("ui.common.add"),schema:this._schema(this.selector),data:{},computeLabel:this._computeLabel,submitText:this.hass.localize("ui.common.add")});if(null===i)return;if(!this.selector.object.multiple)return void(0,c.r)(this,"value-changed",{value:i});const o=(0,n.e)(null!==(t=this.value)&&void 0!==t?t:[]).concat();o.push(i),(0,c.r)(this,"value-changed",{value:o})}async _editItem(e){var t;e.stopPropagation();const i=e.currentTarget.item,o=e.currentTarget.index,r=await(0,h.O)(this,{title:this.hass.localize("ui.common.edit"),schema:this._schema(this.selector),data:i,computeLabel:this._computeLabel,submitText:this.hass.localize("ui.common.save")});if(null===r)return;if(!this.selector.object.multiple)return void(0,c.r)(this,"value-changed",{value:r});const a=(0,n.e)(null!==(t=this.value)&&void 0!==t?t:[]).concat();a[o]=r,(0,c.r)(this,"value-changed",{value:a})}_deleteItem(e){var t;e.stopPropagation();const i=e.currentTarget.index;if(!this.selector.object.multiple)return void(0,c.r)(this,"value-changed",{value:void 0});const o=(0,n.e)(null!==(t=this.value)&&void 0!==t?t:[]).concat();o.splice(i,1),(0,c.r)(this,"value-changed",{value:o})}updated(e){super.updated(e),e.has("value")&&!this._valueChangedFromChild&&this._yamlEditor&&!(0,p.b)(this.value,e.get("value"))&&this._yamlEditor.setValue(this.value),this._valueChangedFromChild=!1}_handleChange(e){e.stopPropagation(),this._valueChangedFromChild=!0;const t=e.target.value;e.target.isValid&&this.value!==t&&(0,c.r)(this,"value-changed",{value:t})}static get styles(){return[(0,a.AH)(w||(w=H`
        ha-md-list {
          gap: 8px;
        }
        ha-md-list-item {
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          --ha-md-list-item-gap: 0;
          --md-list-item-top-space: 0;
          --md-list-item-bottom-space: 0;
          --md-list-item-leading-space: 12px;
          --md-list-item-trailing-space: 4px;
          --md-list-item-two-line-container-height: 48px;
          --md-list-item-one-line-container-height: 48px;
        }
        .handle {
          cursor: move;
          padding: 8px;
          margin-inline-start: -8px;
        }
        label {
          margin-bottom: 8px;
          display: block;
        }
        ha-md-list-item .label,
        ha-md-list-item .description {
          text-overflow: ellipsis;
          overflow: hidden;
          white-space: nowrap;
        }
      `))]}constructor(...e){super(...e),this.disabled=!1,this.required=!0,this._valueChangedFromChild=!1,this._computeLabel=e=>{var t,i;const o=null===(t=this.selector.object)||void 0===t?void 0:t.translation_key;if(this.localizeValue&&o){const t=this.localizeValue(`${o}.fields.${e.name}`);if(t)return t}return(null===(i=this.selector.object)||void 0===i||null===(i=i.fields)||void 0===i||null===(i=i[e.name])||void 0===i?void 0:i.label)||e.name},this._schema=(0,l.A)((e=>e.object&&e.object.fields?Object.entries(e.object.fields).map((([e,t])=>{var i;return{name:e,selector:t.selector,required:null!==(i=t.required)&&void 0!==i&&i}})):[]))}}(0,r.__decorate)([(0,s.MZ)({attribute:!1})],k.prototype,"hass",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],k.prototype,"selector",void 0),(0,r.__decorate)([(0,s.MZ)()],k.prototype,"value",void 0),(0,r.__decorate)([(0,s.MZ)()],k.prototype,"label",void 0),(0,r.__decorate)([(0,s.MZ)()],k.prototype,"helper",void 0),(0,r.__decorate)([(0,s.MZ)()],k.prototype,"placeholder",void 0),(0,r.__decorate)([(0,s.MZ)({type:Boolean})],k.prototype,"disabled",void 0),(0,r.__decorate)([(0,s.MZ)({type:Boolean})],k.prototype,"required",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],k.prototype,"localizeValue",void 0),(0,r.__decorate)([(0,s.P)("ha-yaml-editor",!0)],k.prototype,"_yamlEditor",void 0),k=(0,r.__decorate)([(0,s.EM)("ha-selector-object")],k),o()}catch(v){o(v)}}))},79080:function(e,t,i){i.a(e,(async function(e,t){try{i(35748),i(5934),i(95013);var o=i(69868),r=i(90227),a=i(84922),s=i(11991),l=i(73120),n=i(83566),c=i(84810),d=i(72698),h=i(5503),u=i(76943),p=(i(23749),e([c,u]));[c,u]=p.then?(await p)():p;let m,v,f,y,b,_,g=e=>e;const $=e=>{if("object"!=typeof e||null===e)return!1;for(const t in e)if(Object.prototype.hasOwnProperty.call(e,t))return!1;return!0};class M extends a.WF{setValue(e){try{this._yaml=$(e)?"":(0,r.Bh)(e,{schema:this.yamlSchema,quotingType:'"',noRefs:!0})}catch(t){console.error(t,e),alert(`There was an error converting to YAML: ${t}`)}}firstUpdated(){void 0!==this.defaultValue&&this.setValue(this.defaultValue)}willUpdate(e){super.willUpdate(e),this.autoUpdate&&e.has("value")&&this.setValue(this.value)}focus(){var e,t;null!==(e=this._codeEditor)&&void 0!==e&&e.codemirror&&(null===(t=this._codeEditor)||void 0===t||t.codemirror.focus())}render(){return void 0===this._yaml?a.s6:(0,a.qy)(m||(m=g`
      ${0}
      <ha-code-editor
        .hass=${0}
        .value=${0}
        .readOnly=${0}
        .disableFullscreen=${0}
        mode="yaml"
        autocomplete-entities
        autocomplete-icons
        .error=${0}
        @value-changed=${0}
        @blur=${0}
        dir="ltr"
      ></ha-code-editor>
      ${0}
      ${0}
    `),this.label?(0,a.qy)(v||(v=g`<p>${0}${0}</p>`),this.label,this.required?" *":""):a.s6,this.hass,this._yaml,this.readOnly,this.disableFullscreen,!1===this.isValid,this._onChange,this._onBlur,this._showingError?(0,a.qy)(f||(f=g`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):a.s6,this.copyClipboard||this.hasExtraActions?(0,a.qy)(y||(y=g`
            <div class="card-actions">
              ${0}
              <slot name="extra-actions"></slot>
            </div>
          `),this.copyClipboard?(0,a.qy)(b||(b=g`
                    <ha-button appearance="plain" @click=${0}>
                      ${0}
                    </ha-button>
                  `),this._copyYaml,this.hass.localize("ui.components.yaml-editor.copy_to_clipboard")):a.s6):a.s6)}_onChange(e){let t;e.stopPropagation(),this._yaml=e.detail.value;let i,o=!0;if(this._yaml)try{t=(0,r.Hh)(this._yaml,{schema:this.yamlSchema})}catch(a){o=!1,i=`${this.hass.localize("ui.components.yaml-editor.error",{reason:a.reason})}${a.mark?` (${this.hass.localize("ui.components.yaml-editor.error_location",{line:a.mark.line+1,column:a.mark.column+1})})`:""}`}else t={};this._error=null!=i?i:"",o&&(this._showingError=!1),this.value=t,this.isValid=o,(0,l.r)(this,"value-changed",{value:t,isValid:o,errorMsg:i})}_onBlur(){this.showErrors&&this._error&&(this._showingError=!0)}get yaml(){return this._yaml}async _copyYaml(){this.yaml&&(await(0,h.l)(this.yaml),(0,d.P)(this,{message:this.hass.localize("ui.common.copied_clipboard")}))}static get styles(){return[n.RF,(0,a.AH)(_||(_=g`
        .card-actions {
          border-radius: var(
            --actions-border-radius,
            0px 0px var(--ha-card-border-radius, 12px)
              var(--ha-card-border-radius, 12px)
          );
          border: 1px solid var(--divider-color);
          padding: 5px 16px;
        }
        ha-code-editor {
          flex-grow: 1;
          min-height: 0;
        }
      `))]}constructor(...e){super(...e),this.yamlSchema=r.my,this.isValid=!0,this.autoUpdate=!1,this.readOnly=!1,this.disableFullscreen=!1,this.required=!1,this.copyClipboard=!1,this.hasExtraActions=!1,this.showErrors=!0,this._yaml="",this._error="",this._showingError=!1}}(0,o.__decorate)([(0,s.MZ)({attribute:!1})],M.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)()],M.prototype,"value",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],M.prototype,"yamlSchema",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],M.prototype,"defaultValue",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"is-valid",type:Boolean})],M.prototype,"isValid",void 0),(0,o.__decorate)([(0,s.MZ)()],M.prototype,"label",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"auto-update",type:Boolean})],M.prototype,"autoUpdate",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"read-only",type:Boolean})],M.prototype,"readOnly",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"disable-fullscreen"})],M.prototype,"disableFullscreen",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],M.prototype,"required",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"copy-clipboard",type:Boolean})],M.prototype,"copyClipboard",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"has-extra-actions",type:Boolean})],M.prototype,"hasExtraActions",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"show-errors",type:Boolean})],M.prototype,"showErrors",void 0),(0,o.__decorate)([(0,s.wk)()],M.prototype,"_yaml",void 0),(0,o.__decorate)([(0,s.wk)()],M.prototype,"_error",void 0),(0,o.__decorate)([(0,s.wk)()],M.prototype,"_showingError",void 0),(0,o.__decorate)([(0,s.P)("ha-code-editor")],M.prototype,"_codeEditor",void 0),M=(0,o.__decorate)([(0,s.EM)("ha-yaml-editor")],M),t()}catch(m){t(m)}}))},66100:function(e,t,i){i.d(t,{C:function(){return s}});i(65315),i(37089),i(47849);var o=i(26846),r=i(22441),a=i(18390);const s=(e,t,i)=>{if(null==t)return"";if(!i)return(0,o.e)(t).join(", ");if("text"in i){const{prefix:e,suffix:r}=i.text||{};return(0,o.e)(t).map((t=>`${e||""}${t}${r||""}`)).join(", ")}if("number"in i){const{unit_of_measurement:r}=i.number||{};return(0,o.e)(t).map((t=>{const i=Number(t);return isNaN(i)?t:r?`${i}${(0,a.A)(r,e.locale)}${r}`:i.toString()})).join(", ")}if("floor"in i){return(0,o.e)(t).map((t=>{const i=e.floors[t];return i&&i.name||t})).join(", ")}if("area"in i){return(0,o.e)(t).map((t=>{const i=e.areas[t];return i?(0,r.A)(i):t})).join(", ")}if("entity"in i){return(0,o.e)(t).map((t=>{const i=e.states[t];if(!i)return t;return e.formatEntityName(i,["device","entity"]," ")||t})).join(", ")}if("device"in i){return(0,o.e)(t).map((t=>{const i=e.devices[t];return i&&i.name||t})).join(", ")}return(0,o.e)(t).join(", ")}},33728:function(e,t,i){i.d(t,{O:function(){return r}});i(35748),i(12977),i(5934),i(95013);var o=i(73120);const r=(e,t)=>new Promise((r=>{const a=t.cancel,s=t.submit;(0,o.r)(e,"show-dialog",{dialogTag:"dialog-form",dialogImport:()=>i.e("5413").then(i.bind(i,42612)),dialogParams:Object.assign(Object.assign({},t),{},{cancel:()=>{r(null),a&&a()},submit:e=>{r(e),s&&s(e)}})})}))},72698:function(e,t,i){i.d(t,{P:function(){return r}});var o=i(73120);const r=(e,t)=>(0,o.r)(e,"hass-notification",t)}}]);
//# sourceMappingURL=5857.ed3bd6abe578fbc6.js.map