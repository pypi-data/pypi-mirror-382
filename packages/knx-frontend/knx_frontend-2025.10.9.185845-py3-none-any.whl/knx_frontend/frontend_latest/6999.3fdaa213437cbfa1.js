export const __webpack_id__="6999";export const __webpack_ids__=["6999"];export const __webpack_modules__={47379:function(e,t,i){i.d(t,{u:()=>a});var s=i(90321);const a=e=>{return t=e.entity_id,void 0===(i=e.attributes).friendly_name?(0,s.Y)(t).replace(/_/g," "):(i.friendly_name??"").toString();var t,i}},30874:function(e,t,i){i.r(t),i.d(t,{HaSTTSelector:()=>c});var s=i(69868),a=i(84922),o=i(11991),n=i(73120),r=i(20674),d=i(47379),l=i(24802),u=i(32512),h=(i(25223),i(37207),i(92830));const _="__NONE_OPTION__";class p extends a.WF{render(){if(!this._engines)return a.s6;let e=this.value;if(!e&&this.required){for(const t of Object.values(this.hass.entities))if("cloud"===t.platform&&"stt"===(0,h.m)(t.entity_id)){e=t.entity_id;break}if(!e)for(const t of this._engines)if(0!==t?.supported_languages?.length){e=t.engine_id;break}}return e||(e=_),a.qy`
      <ha-select
        .label=${this.label||this.hass.localize("ui.components.stt-picker.stt")}
        .value=${e}
        .required=${this.required}
        .disabled=${this.disabled}
        @selected=${this._changed}
        @closed=${r.d}
        fixedMenuPosition
        naturalMenuWidth
      >
        ${this.required?a.s6:a.qy`<ha-list-item .value=${_}>
              ${this.hass.localize("ui.components.stt-picker.none")}
            </ha-list-item>`}
        ${this._engines.map((t=>{if(t.deprecated&&t.engine_id!==e)return a.s6;let i;if(t.engine_id.includes(".")){const e=this.hass.states[t.engine_id];i=e?(0,d.u)(e):t.engine_id}else i=t.name||t.engine_id;return a.qy`<ha-list-item
            .value=${t.engine_id}
            .disabled=${0===t.supported_languages?.length}
          >
            ${i}
          </ha-list-item>`}))}
      </ha-select>
    `}willUpdate(e){super.willUpdate(e),this.hasUpdated?e.has("language")&&this._debouncedUpdateEngines():this._updateEngines()}async _updateEngines(){if(this._engines=(await(0,u.T)(this.hass,this.language,this.hass.config.country||void 0)).providers,!this.value)return;const e=this._engines.find((e=>e.engine_id===this.value));(0,n.r)(this,"supported-languages-changed",{value:e?.supported_languages}),e&&0!==e.supported_languages?.length||(this.value=void 0,(0,n.r)(this,"value-changed",{value:this.value}))}_changed(e){const t=e.target;!this.hass||""===t.value||t.value===this.value||void 0===this.value&&t.value===_||(this.value=t.value===_?void 0:t.value,(0,n.r)(this,"value-changed",{value:this.value}),(0,n.r)(this,"supported-languages-changed",{value:this._engines.find((e=>e.engine_id===this.value))?.supported_languages}))}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this._debouncedUpdateEngines=(0,l.s)((()=>this._updateEngines()),500)}}p.styles=a.AH`
    ha-select {
      width: 100%;
    }
  `,(0,s.__decorate)([(0,o.MZ)()],p.prototype,"value",void 0),(0,s.__decorate)([(0,o.MZ)()],p.prototype,"label",void 0),(0,s.__decorate)([(0,o.MZ)()],p.prototype,"language",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean,reflect:!0})],p.prototype,"disabled",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],p.prototype,"required",void 0),(0,s.__decorate)([(0,o.wk)()],p.prototype,"_engines",void 0),p=(0,s.__decorate)([(0,o.EM)("ha-stt-picker")],p);class c extends a.WF{render(){return a.qy`<ha-stt-picker
      .hass=${this.hass}
      .value=${this.value}
      .label=${this.label}
      .helper=${this.helper}
      .language=${this.selector.stt?.language||this.context?.language}
      .disabled=${this.disabled}
      .required=${this.required}
    ></ha-stt-picker>`}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}c.styles=a.AH`
    ha-stt-picker {
      width: 100%;
    }
  `,(0,s.__decorate)([(0,o.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],c.prototype,"selector",void 0),(0,s.__decorate)([(0,o.MZ)()],c.prototype,"value",void 0),(0,s.__decorate)([(0,o.MZ)()],c.prototype,"label",void 0),(0,s.__decorate)([(0,o.MZ)()],c.prototype,"helper",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],c.prototype,"disabled",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],c.prototype,"required",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],c.prototype,"context",void 0),c=(0,s.__decorate)([(0,o.EM)("ha-selector-stt")],c)},32512:function(e,t,i){i.d(t,{T:()=>s});const s=(e,t,i)=>e.callWS({type:"stt/engine/list",language:t,country:i})}};
//# sourceMappingURL=6999.3fdaa213437cbfa1.js.map