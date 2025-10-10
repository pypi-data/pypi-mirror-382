"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["6999"],{30874:function(e,t,i){i.r(t),i.d(t,{HaSTTSelector:function(){return k}});i(35748),i(95013);var s=i(69868),a=i(84922),n=i(11991),o=(i(79827),i(65315),i(84136),i(37089),i(5934),i(18223),i(73120)),d=i(20674),l=i(47379),r=i(24802),u=i(32512),h=(i(25223),i(37207),i(92830));let p,c,_,v,g=e=>e;const y="__NONE_OPTION__";class b extends a.WF{render(){if(!this._engines)return a.s6;let e=this.value;if(!e&&this.required){for(const t of Object.values(this.hass.entities))if("cloud"===t.platform&&"stt"===(0,h.m)(t.entity_id)){e=t.entity_id;break}if(!e)for(const i of this._engines){var t;if(0!==(null==i||null===(t=i.supported_languages)||void 0===t?void 0:t.length)){e=i.engine_id;break}}}return e||(e=y),(0,a.qy)(p||(p=g`
      <ha-select
        .label=${0}
        .value=${0}
        .required=${0}
        .disabled=${0}
        @selected=${0}
        @closed=${0}
        fixedMenuPosition
        naturalMenuWidth
      >
        ${0}
        ${0}
      </ha-select>
    `),this.label||this.hass.localize("ui.components.stt-picker.stt"),e,this.required,this.disabled,this._changed,d.d,this.required?a.s6:(0,a.qy)(c||(c=g`<ha-list-item .value=${0}>
              ${0}
            </ha-list-item>`),y,this.hass.localize("ui.components.stt-picker.none")),this._engines.map((t=>{var i;if(t.deprecated&&t.engine_id!==e)return a.s6;let s;if(t.engine_id.includes(".")){const e=this.hass.states[t.engine_id];s=e?(0,l.u)(e):t.engine_id}else s=t.name||t.engine_id;return(0,a.qy)(_||(_=g`<ha-list-item
            .value=${0}
            .disabled=${0}
          >
            ${0}
          </ha-list-item>`),t.engine_id,0===(null===(i=t.supported_languages)||void 0===i?void 0:i.length),s)})))}willUpdate(e){super.willUpdate(e),this.hasUpdated?e.has("language")&&this._debouncedUpdateEngines():this._updateEngines()}async _updateEngines(){var e;if(this._engines=(await(0,u.T)(this.hass,this.language,this.hass.config.country||void 0)).providers,!this.value)return;const t=this._engines.find((e=>e.engine_id===this.value));(0,o.r)(this,"supported-languages-changed",{value:null==t?void 0:t.supported_languages}),t&&0!==(null===(e=t.supported_languages)||void 0===e?void 0:e.length)||(this.value=void 0,(0,o.r)(this,"value-changed",{value:this.value}))}_changed(e){var t;const i=e.target;!this.hass||""===i.value||i.value===this.value||void 0===this.value&&i.value===y||(this.value=i.value===y?void 0:i.value,(0,o.r)(this,"value-changed",{value:this.value}),(0,o.r)(this,"supported-languages-changed",{value:null===(t=this._engines.find((e=>e.engine_id===this.value)))||void 0===t?void 0:t.supported_languages}))}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this._debouncedUpdateEngines=(0,r.s)((()=>this._updateEngines()),500)}}b.styles=(0,a.AH)(v||(v=g`
    ha-select {
      width: 100%;
    }
  `)),(0,s.__decorate)([(0,n.MZ)()],b.prototype,"value",void 0),(0,s.__decorate)([(0,n.MZ)()],b.prototype,"label",void 0),(0,s.__decorate)([(0,n.MZ)()],b.prototype,"language",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],b.prototype,"disabled",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],b.prototype,"required",void 0),(0,s.__decorate)([(0,n.wk)()],b.prototype,"_engines",void 0),b=(0,s.__decorate)([(0,n.EM)("ha-stt-picker")],b);let f,$,M=e=>e;class k extends a.WF{render(){var e,t;return(0,a.qy)(f||(f=M`<ha-stt-picker
      .hass=${0}
      .value=${0}
      .label=${0}
      .helper=${0}
      .language=${0}
      .disabled=${0}
      .required=${0}
    ></ha-stt-picker>`),this.hass,this.value,this.label,this.helper,(null===(e=this.selector.stt)||void 0===e?void 0:e.language)||(null===(t=this.context)||void 0===t?void 0:t.language),this.disabled,this.required)}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}k.styles=(0,a.AH)($||($=M`
    ha-stt-picker {
      width: 100%;
    }
  `)),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],k.prototype,"hass",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],k.prototype,"selector",void 0),(0,s.__decorate)([(0,n.MZ)()],k.prototype,"value",void 0),(0,s.__decorate)([(0,n.MZ)()],k.prototype,"label",void 0),(0,s.__decorate)([(0,n.MZ)()],k.prototype,"helper",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],k.prototype,"disabled",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],k.prototype,"required",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],k.prototype,"context",void 0),k=(0,s.__decorate)([(0,n.EM)("ha-selector-stt")],k)},32512:function(e,t,i){i.d(t,{T:function(){return s}});const s=(e,t,i)=>e.callWS({type:"stt/engine/list",language:t,country:i})}}]);
//# sourceMappingURL=6999.d0ce02cf96bc8058.js.map