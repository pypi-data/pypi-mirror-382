export const __webpack_id__="5857";export const __webpack_ids__=["5857"];export const __webpack_modules__={3371:function(e,t,i){i.d(t,{d:()=>o});const o=e=>{switch(e.language){case"cs":case"de":case"fi":case"fr":case"sk":case"sv":return" ";default:return""}}},18390:function(e,t,i){i.d(t,{A:()=>a});var o=i(3371);const a=(e,t)=>"°"===e?"":t&&"%"===e?(0,o.d)(t):" "},55266:function(e,t,i){i.d(t,{b:()=>o});const o=(e,t)=>{if(e===t)return!0;if(e&&t&&"object"==typeof e&&"object"==typeof t){if(e.constructor!==t.constructor)return!1;let i,a;if(Array.isArray(e)){if(a=e.length,a!==t.length)return!1;for(i=a;0!=i--;)if(!o(e[i],t[i]))return!1;return!0}if(e instanceof Map&&t instanceof Map){if(e.size!==t.size)return!1;for(i of e.entries())if(!t.has(i[0]))return!1;for(i of e.entries())if(!o(i[1],t.get(i[0])))return!1;return!0}if(e instanceof Set&&t instanceof Set){if(e.size!==t.size)return!1;for(i of e.entries())if(!t.has(i[0]))return!1;return!0}if(ArrayBuffer.isView(e)&&ArrayBuffer.isView(t)){if(a=e.length,a!==t.length)return!1;for(i=a;0!=i--;)if(e[i]!==t[i])return!1;return!0}if(e.constructor===RegExp)return e.source===t.source&&e.flags===t.flags;if(e.valueOf!==Object.prototype.valueOf)return e.valueOf()===t.valueOf();if(e.toString!==Object.prototype.toString)return e.toString()===t.toString();const r=Object.keys(e);if(a=r.length,a!==Object.keys(t).length)return!1;for(i=a;0!=i--;)if(!Object.prototype.hasOwnProperty.call(t,r[i]))return!1;for(i=a;0!=i--;){const a=r[i];if(!o(e[a],t[a]))return!1}return!0}return e!=e&&t!=t}},41480:function(e,t,i){i.a(e,(async function(e,o){try{i.r(t),i.d(t,{HaObjectSelector:()=>f});var a=i(69868),r=i(84922),s=i(11991),l=i(65940),n=i(26846),c=i(73120),d=i(66100),h=i(33728),u=(i(20014),i(5803),i(98343),i(8115),i(79080)),p=i(55266),m=e([u]);u=(m.then?(await m)():m)[0];const _="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",y="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z",b="M7,19V17H9V19H7M11,19V17H13V19H11M15,19V17H17V19H15M7,15V13H9V15H7M11,15V13H13V15H11M15,15V13H17V15H15M7,11V9H9V11H7M11,11V9H13V11H11M15,11V9H17V11H15M7,7V5H9V7H7M11,7V5H13V7H11M15,7V5H17V7H15Z",v="M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z";class f extends r.WF{_renderItem(e,t){const i=this.selector.object.label_field||Object.keys(this.selector.object.fields)[0],o=this.selector.object.fields[i].selector,a=o?(0,d.C)(this.hass,e[i],o):"";let s="";const l=this.selector.object.description_field;if(l){const t=this.selector.object.fields[l].selector;s=t?(0,d.C)(this.hass,e[l],t):""}const n=this.selector.object.multiple||!1,c=this.selector.object.multiple||!1;return r.qy`
      <ha-md-list-item class="item">
        ${n?r.qy`
              <ha-svg-icon
                class="handle"
                .path=${b}
                slot="start"
              ></ha-svg-icon>
            `:r.s6}
        <div slot="headline" class="label">${a}</div>
        ${s?r.qy`<div slot="supporting-text" class="description">
              ${s}
            </div>`:r.s6}
        <ha-icon-button
          slot="end"
          .item=${e}
          .index=${t}
          .label=${this.hass.localize("ui.common.edit")}
          .path=${v}
          @click=${this._editItem}
        ></ha-icon-button>
        <ha-icon-button
          slot="end"
          .index=${t}
          .label=${this.hass.localize("ui.common.delete")}
          .path=${c?y:_}
          @click=${this._deleteItem}
        ></ha-icon-button>
      </ha-md-list-item>
    `}render(){if(this.selector.object?.fields){if(this.selector.object.multiple){const e=(0,n.e)(this.value??[]);return r.qy`
          ${this.label?r.qy`<label>${this.label}</label>`:r.s6}
          <div class="items-container">
            <ha-sortable
              handle-selector=".handle"
              draggable-selector=".item"
              @item-moved=${this._itemMoved}
            >
              <ha-md-list>
                ${e.map(((e,t)=>this._renderItem(e,t)))}
              </ha-md-list>
            </ha-sortable>
            <ha-button appearance="filled" @click=${this._addItem}>
              ${this.hass.localize("ui.common.add")}
            </ha-button>
          </div>
        `}return r.qy`
        ${this.label?r.qy`<label>${this.label}</label>`:r.s6}
        <div class="items-container">
          ${this.value?r.qy`<ha-md-list>
                ${this._renderItem(this.value,0)}
              </ha-md-list>`:r.qy`
                <ha-button appearance="filled" @click=${this._addItem}>
                  ${this.hass.localize("ui.common.add")}
                </ha-button>
              `}
        </div>
      `}return r.qy`<ha-yaml-editor
        .hass=${this.hass}
        .readonly=${this.disabled}
        .label=${this.label}
        .required=${this.required}
        .placeholder=${this.placeholder}
        .defaultValue=${this.value}
        @value-changed=${this._handleChange}
      ></ha-yaml-editor>
      ${this.helper?r.qy`<ha-input-helper-text .disabled=${this.disabled}
            >${this.helper}</ha-input-helper-text
          >`:""} `}_itemMoved(e){e.stopPropagation();const t=e.detail.newIndex,i=e.detail.oldIndex;if(!this.selector.object.multiple)return;const o=(0,n.e)(this.value??[]).concat(),a=o.splice(i,1)[0];o.splice(t,0,a),(0,c.r)(this,"value-changed",{value:o})}async _addItem(e){e.stopPropagation();const t=await(0,h.O)(this,{title:this.hass.localize("ui.common.add"),schema:this._schema(this.selector),data:{},computeLabel:this._computeLabel,submitText:this.hass.localize("ui.common.add")});if(null===t)return;if(!this.selector.object.multiple)return void(0,c.r)(this,"value-changed",{value:t});const i=(0,n.e)(this.value??[]).concat();i.push(t),(0,c.r)(this,"value-changed",{value:i})}async _editItem(e){e.stopPropagation();const t=e.currentTarget.item,i=e.currentTarget.index,o=await(0,h.O)(this,{title:this.hass.localize("ui.common.edit"),schema:this._schema(this.selector),data:t,computeLabel:this._computeLabel,submitText:this.hass.localize("ui.common.save")});if(null===o)return;if(!this.selector.object.multiple)return void(0,c.r)(this,"value-changed",{value:o});const a=(0,n.e)(this.value??[]).concat();a[i]=o,(0,c.r)(this,"value-changed",{value:a})}_deleteItem(e){e.stopPropagation();const t=e.currentTarget.index;if(!this.selector.object.multiple)return void(0,c.r)(this,"value-changed",{value:void 0});const i=(0,n.e)(this.value??[]).concat();i.splice(t,1),(0,c.r)(this,"value-changed",{value:i})}updated(e){super.updated(e),e.has("value")&&!this._valueChangedFromChild&&this._yamlEditor&&!(0,p.b)(this.value,e.get("value"))&&this._yamlEditor.setValue(this.value),this._valueChangedFromChild=!1}_handleChange(e){e.stopPropagation(),this._valueChangedFromChild=!0;const t=e.target.value;e.target.isValid&&this.value!==t&&(0,c.r)(this,"value-changed",{value:t})}static get styles(){return[r.AH`
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
      `]}constructor(...e){super(...e),this.disabled=!1,this.required=!0,this._valueChangedFromChild=!1,this._computeLabel=e=>{const t=this.selector.object?.translation_key;if(this.localizeValue&&t){const i=this.localizeValue(`${t}.fields.${e.name}`);if(i)return i}return this.selector.object?.fields?.[e.name]?.label||e.name},this._schema=(0,l.A)((e=>e.object&&e.object.fields?Object.entries(e.object.fields).map((([e,t])=>({name:e,selector:t.selector,required:t.required??!1}))):[]))}}(0,a.__decorate)([(0,s.MZ)({attribute:!1})],f.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],f.prototype,"selector",void 0),(0,a.__decorate)([(0,s.MZ)()],f.prototype,"value",void 0),(0,a.__decorate)([(0,s.MZ)()],f.prototype,"label",void 0),(0,a.__decorate)([(0,s.MZ)()],f.prototype,"helper",void 0),(0,a.__decorate)([(0,s.MZ)()],f.prototype,"placeholder",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],f.prototype,"disabled",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],f.prototype,"required",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],f.prototype,"localizeValue",void 0),(0,a.__decorate)([(0,s.P)("ha-yaml-editor",!0)],f.prototype,"_yamlEditor",void 0),f=(0,a.__decorate)([(0,s.EM)("ha-selector-object")],f),o()}catch(_){o(_)}}))},79080:function(e,t,i){i.a(e,(async function(e,t){try{var o=i(69868),a=i(90227),r=i(84922),s=i(11991),l=i(73120),n=i(83566),c=i(84810),d=i(72698),h=i(5503),u=i(76943),p=(i(23749),e([c,u]));[c,u]=p.then?(await p)():p;const m=e=>{if("object"!=typeof e||null===e)return!1;for(const t in e)if(Object.prototype.hasOwnProperty.call(e,t))return!1;return!0};class _ extends r.WF{setValue(e){try{this._yaml=m(e)?"":(0,a.Bh)(e,{schema:this.yamlSchema,quotingType:'"',noRefs:!0})}catch(t){console.error(t,e),alert(`There was an error converting to YAML: ${t}`)}}firstUpdated(){void 0!==this.defaultValue&&this.setValue(this.defaultValue)}willUpdate(e){super.willUpdate(e),this.autoUpdate&&e.has("value")&&this.setValue(this.value)}focus(){this._codeEditor?.codemirror&&this._codeEditor?.codemirror.focus()}render(){return void 0===this._yaml?r.s6:r.qy`
      ${this.label?r.qy`<p>${this.label}${this.required?" *":""}</p>`:r.s6}
      <ha-code-editor
        .hass=${this.hass}
        .value=${this._yaml}
        .readOnly=${this.readOnly}
        .disableFullscreen=${this.disableFullscreen}
        mode="yaml"
        autocomplete-entities
        autocomplete-icons
        .error=${!1===this.isValid}
        @value-changed=${this._onChange}
        @blur=${this._onBlur}
        dir="ltr"
      ></ha-code-editor>
      ${this._showingError?r.qy`<ha-alert alert-type="error">${this._error}</ha-alert>`:r.s6}
      ${this.copyClipboard||this.hasExtraActions?r.qy`
            <div class="card-actions">
              ${this.copyClipboard?r.qy`
                    <ha-button appearance="plain" @click=${this._copyYaml}>
                      ${this.hass.localize("ui.components.yaml-editor.copy_to_clipboard")}
                    </ha-button>
                  `:r.s6}
              <slot name="extra-actions"></slot>
            </div>
          `:r.s6}
    `}_onChange(e){let t;e.stopPropagation(),this._yaml=e.detail.value;let i,o=!0;if(this._yaml)try{t=(0,a.Hh)(this._yaml,{schema:this.yamlSchema})}catch(r){o=!1,i=`${this.hass.localize("ui.components.yaml-editor.error",{reason:r.reason})}${r.mark?` (${this.hass.localize("ui.components.yaml-editor.error_location",{line:r.mark.line+1,column:r.mark.column+1})})`:""}`}else t={};this._error=i??"",o&&(this._showingError=!1),this.value=t,this.isValid=o,(0,l.r)(this,"value-changed",{value:t,isValid:o,errorMsg:i})}_onBlur(){this.showErrors&&this._error&&(this._showingError=!0)}get yaml(){return this._yaml}async _copyYaml(){this.yaml&&(await(0,h.l)(this.yaml),(0,d.P)(this,{message:this.hass.localize("ui.common.copied_clipboard")}))}static get styles(){return[n.RF,r.AH`
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
      `]}constructor(...e){super(...e),this.yamlSchema=a.my,this.isValid=!0,this.autoUpdate=!1,this.readOnly=!1,this.disableFullscreen=!1,this.required=!1,this.copyClipboard=!1,this.hasExtraActions=!1,this.showErrors=!0,this._yaml="",this._error="",this._showingError=!1}}(0,o.__decorate)([(0,s.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)()],_.prototype,"value",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],_.prototype,"yamlSchema",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],_.prototype,"defaultValue",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"is-valid",type:Boolean})],_.prototype,"isValid",void 0),(0,o.__decorate)([(0,s.MZ)()],_.prototype,"label",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"auto-update",type:Boolean})],_.prototype,"autoUpdate",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"read-only",type:Boolean})],_.prototype,"readOnly",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"disable-fullscreen"})],_.prototype,"disableFullscreen",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],_.prototype,"required",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"copy-clipboard",type:Boolean})],_.prototype,"copyClipboard",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"has-extra-actions",type:Boolean})],_.prototype,"hasExtraActions",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"show-errors",type:Boolean})],_.prototype,"showErrors",void 0),(0,o.__decorate)([(0,s.wk)()],_.prototype,"_yaml",void 0),(0,o.__decorate)([(0,s.wk)()],_.prototype,"_error",void 0),(0,o.__decorate)([(0,s.wk)()],_.prototype,"_showingError",void 0),(0,o.__decorate)([(0,s.P)("ha-code-editor")],_.prototype,"_codeEditor",void 0),_=(0,o.__decorate)([(0,s.EM)("ha-yaml-editor")],_),t()}catch(m){t(m)}}))},66100:function(e,t,i){i.d(t,{C:()=>s});var o=i(26846),a=i(22441),r=i(18390);const s=(e,t,i)=>{if(null==t)return"";if(!i)return(0,o.e)(t).join(", ");if("text"in i){const{prefix:e,suffix:a}=i.text||{};return(0,o.e)(t).map((t=>`${e||""}${t}${a||""}`)).join(", ")}if("number"in i){const{unit_of_measurement:a}=i.number||{};return(0,o.e)(t).map((t=>{const i=Number(t);return isNaN(i)?t:a?`${i}${(0,r.A)(a,e.locale)}${a}`:i.toString()})).join(", ")}if("floor"in i){return(0,o.e)(t).map((t=>{const i=e.floors[t];return i&&i.name||t})).join(", ")}if("area"in i){return(0,o.e)(t).map((t=>{const i=e.areas[t];return i?(0,a.A)(i):t})).join(", ")}if("entity"in i){return(0,o.e)(t).map((t=>{const i=e.states[t];if(!i)return t;return e.formatEntityName(i,["device","entity"]," ")||t})).join(", ")}if("device"in i){return(0,o.e)(t).map((t=>{const i=e.devices[t];return i&&i.name||t})).join(", ")}return(0,o.e)(t).join(", ")}},33728:function(e,t,i){i.d(t,{O:()=>a});var o=i(73120);const a=(e,t)=>new Promise((a=>{const r=t.cancel,s=t.submit;(0,o.r)(e,"show-dialog",{dialogTag:"dialog-form",dialogImport:()=>i.e("5413").then(i.bind(i,42612)),dialogParams:{...t,cancel:()=>{a(null),r&&r()},submit:e=>{a(e),s&&s(e)}}})}))},72698:function(e,t,i){i.d(t,{P:()=>a});var o=i(73120);const a=(e,t)=>(0,o.r)(e,"hass-notification",t)}};
//# sourceMappingURL=5857.c39d276be4d978f0.js.map