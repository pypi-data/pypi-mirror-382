export const __webpack_id__="2566";export const __webpack_ids__=["2566"];export const __webpack_modules__={69205:function(e,t,i){i.r(t),i.d(t,{HaTTSVoiceSelector:()=>d});var s=i(69868),a=i(84922),o=i(11991);i(52428);class d extends a.WF{render(){return a.qy`<ha-tts-voice-picker
      .hass=${this.hass}
      .value=${this.value}
      .label=${this.label}
      .helper=${this.helper}
      .language=${this.selector.tts_voice?.language||this.context?.language}
      .engineId=${this.selector.tts_voice?.engineId||this.context?.engineId}
      .disabled=${this.disabled}
      .required=${this.required}
    ></ha-tts-voice-picker>`}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}d.styles=a.AH`
    ha-tts-picker {
      width: 100%;
    }
  `,(0,s.__decorate)([(0,o.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],d.prototype,"selector",void 0),(0,s.__decorate)([(0,o.MZ)()],d.prototype,"value",void 0),(0,s.__decorate)([(0,o.MZ)()],d.prototype,"label",void 0),(0,s.__decorate)([(0,o.MZ)()],d.prototype,"helper",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],d.prototype,"disabled",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],d.prototype,"required",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],d.prototype,"context",void 0),d=(0,s.__decorate)([(0,o.EM)("ha-selector-tts_voice")],d)},52428:function(e,t,i){var s=i(69868),a=i(84922),o=i(11991),d=i(73120),l=i(20674),c=i(24802),r=i(87608);i(25223),i(37207);const h="__NONE_OPTION__";class _ extends a.WF{render(){if(!this._voices)return a.s6;const e=this.value??(this.required?this._voices[0]?.voice_id:h);return a.qy`
      <ha-select
        .label=${this.label||this.hass.localize("ui.components.tts-voice-picker.voice")}
        .value=${e}
        .required=${this.required}
        .disabled=${this.disabled}
        @selected=${this._changed}
        @closed=${l.d}
        fixedMenuPosition
        naturalMenuWidth
      >
        ${this.required?a.s6:a.qy`<ha-list-item .value=${h}>
              ${this.hass.localize("ui.components.tts-voice-picker.none")}
            </ha-list-item>`}
        ${this._voices.map((e=>a.qy`<ha-list-item .value=${e.voice_id}>
              ${e.name}
            </ha-list-item>`))}
      </ha-select>
    `}willUpdate(e){super.willUpdate(e),this.hasUpdated?(e.has("language")||e.has("engineId"))&&this._debouncedUpdateVoices():this._updateVoices()}async _updateVoices(){this.engineId&&this.language?(this._voices=(await(0,r.z3)(this.hass,this.engineId,this.language)).voices,this.value&&(this._voices&&this._voices.find((e=>e.voice_id===this.value))||(this.value=void 0,(0,d.r)(this,"value-changed",{value:this.value})))):this._voices=void 0}updated(e){super.updated(e),e.has("_voices")&&this._select?.value!==this.value&&(this._select?.layoutOptions(),(0,d.r)(this,"value-changed",{value:this._select?.value}))}_changed(e){const t=e.target;!this.hass||""===t.value||t.value===this.value||void 0===this.value&&t.value===h||(this.value=t.value===h?void 0:t.value,(0,d.r)(this,"value-changed",{value:this.value}))}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this._debouncedUpdateVoices=(0,c.s)((()=>this._updateVoices()),500)}}_.styles=a.AH`
    ha-select {
      width: 100%;
    }
  `,(0,s.__decorate)([(0,o.MZ)()],_.prototype,"value",void 0),(0,s.__decorate)([(0,o.MZ)()],_.prototype,"label",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],_.prototype,"engineId",void 0),(0,s.__decorate)([(0,o.MZ)()],_.prototype,"language",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean,reflect:!0})],_.prototype,"disabled",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],_.prototype,"required",void 0),(0,s.__decorate)([(0,o.wk)()],_.prototype,"_voices",void 0),(0,s.__decorate)([(0,o.P)("ha-select")],_.prototype,"_select",void 0),_=(0,s.__decorate)([(0,o.EM)("ha-tts-voice-picker")],_)},87608:function(e,t,i){i.d(t,{EF:()=>d,S_:()=>s,Xv:()=>l,ni:()=>o,u1:()=>c,z3:()=>r});const s=(e,t)=>e.callApi("POST","tts_get_url",t),a="media-source://tts/",o=e=>e.startsWith(a),d=e=>e.substring(19),l=(e,t,i)=>e.callWS({type:"tts/engine/list",language:t,country:i}),c=(e,t)=>e.callWS({type:"tts/engine/get",engine_id:t}),r=(e,t,i)=>e.callWS({type:"tts/engine/voices",engine_id:t,language:i})}};
//# sourceMappingURL=2566.f854004b15e80b38.js.map