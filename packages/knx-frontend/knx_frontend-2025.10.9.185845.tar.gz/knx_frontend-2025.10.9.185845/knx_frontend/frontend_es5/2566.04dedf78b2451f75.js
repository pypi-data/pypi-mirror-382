"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2566"],{69205:function(e,t,i){i.r(t),i.d(t,{HaTTSVoiceSelector:function(){return n}});i(35748),i(95013);var o=i(69868),s=i(84922),a=i(11991);i(52428);let d,l,r=e=>e;class n extends s.WF{render(){var e,t,i,o;return(0,s.qy)(d||(d=r`<ha-tts-voice-picker
      .hass=${0}
      .value=${0}
      .label=${0}
      .helper=${0}
      .language=${0}
      .engineId=${0}
      .disabled=${0}
      .required=${0}
    ></ha-tts-voice-picker>`),this.hass,this.value,this.label,this.helper,(null===(e=this.selector.tts_voice)||void 0===e?void 0:e.language)||(null===(t=this.context)||void 0===t?void 0:t.language),(null===(i=this.selector.tts_voice)||void 0===i?void 0:i.engineId)||(null===(o=this.context)||void 0===o?void 0:o.engineId),this.disabled,this.required)}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}n.styles=(0,s.AH)(l||(l=r`
    ha-tts-picker {
      width: 100%;
    }
  `)),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],n.prototype,"hass",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],n.prototype,"selector",void 0),(0,o.__decorate)([(0,a.MZ)()],n.prototype,"value",void 0),(0,o.__decorate)([(0,a.MZ)()],n.prototype,"label",void 0),(0,o.__decorate)([(0,a.MZ)()],n.prototype,"helper",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],n.prototype,"disabled",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],n.prototype,"required",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],n.prototype,"context",void 0),n=(0,o.__decorate)([(0,a.EM)("ha-selector-tts_voice")],n)},52428:function(e,t,i){i(35748),i(65315),i(84136),i(37089),i(5934),i(95013);var o=i(69868),s=i(84922),a=i(11991),d=i(73120),l=i(20674),r=i(24802),n=i(87608);i(25223),i(37207);let c,u,h,v,_=e=>e;const p="__NONE_OPTION__";class g extends s.WF{render(){var e,t;if(!this._voices)return s.s6;const i=null!==(e=this.value)&&void 0!==e?e:this.required?null===(t=this._voices[0])||void 0===t?void 0:t.voice_id:p;return(0,s.qy)(c||(c=_`
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
    `),this.label||this.hass.localize("ui.components.tts-voice-picker.voice"),i,this.required,this.disabled,this._changed,l.d,this.required?s.s6:(0,s.qy)(u||(u=_`<ha-list-item .value=${0}>
              ${0}
            </ha-list-item>`),p,this.hass.localize("ui.components.tts-voice-picker.none")),this._voices.map((e=>(0,s.qy)(h||(h=_`<ha-list-item .value=${0}>
              ${0}
            </ha-list-item>`),e.voice_id,e.name))))}willUpdate(e){super.willUpdate(e),this.hasUpdated?(e.has("language")||e.has("engineId"))&&this._debouncedUpdateVoices():this._updateVoices()}async _updateVoices(){this.engineId&&this.language?(this._voices=(await(0,n.z3)(this.hass,this.engineId,this.language)).voices,this.value&&(this._voices&&this._voices.find((e=>e.voice_id===this.value))||(this.value=void 0,(0,d.r)(this,"value-changed",{value:this.value})))):this._voices=void 0}updated(e){var t,i,o;(super.updated(e),e.has("_voices")&&(null===(t=this._select)||void 0===t?void 0:t.value)!==this.value)&&(null===(i=this._select)||void 0===i||i.layoutOptions(),(0,d.r)(this,"value-changed",{value:null===(o=this._select)||void 0===o?void 0:o.value}))}_changed(e){const t=e.target;!this.hass||""===t.value||t.value===this.value||void 0===this.value&&t.value===p||(this.value=t.value===p?void 0:t.value,(0,d.r)(this,"value-changed",{value:this.value}))}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this._debouncedUpdateVoices=(0,r.s)((()=>this._updateVoices()),500)}}g.styles=(0,s.AH)(v||(v=_`
    ha-select {
      width: 100%;
    }
  `)),(0,o.__decorate)([(0,a.MZ)()],g.prototype,"value",void 0),(0,o.__decorate)([(0,a.MZ)()],g.prototype,"label",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],g.prototype,"engineId",void 0),(0,o.__decorate)([(0,a.MZ)()],g.prototype,"language",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean,reflect:!0})],g.prototype,"disabled",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],g.prototype,"required",void 0),(0,o.__decorate)([(0,a.wk)()],g.prototype,"_voices",void 0),(0,o.__decorate)([(0,a.P)("ha-select")],g.prototype,"_select",void 0),g=(0,o.__decorate)([(0,a.EM)("ha-tts-voice-picker")],g)},87608:function(e,t,i){i.d(t,{EF:function(){return d},S_:function(){return o},Xv:function(){return l},ni:function(){return a},u1:function(){return r},z3:function(){return n}});i(56660);const o=(e,t)=>e.callApi("POST","tts_get_url",t),s="media-source://tts/",a=e=>e.startsWith(s),d=e=>e.substring(19),l=(e,t,i)=>e.callWS({type:"tts/engine/list",language:t,country:i}),r=(e,t)=>e.callWS({type:"tts/engine/get",engine_id:t}),n=(e,t,i)=>e.callWS({type:"tts/engine/voices",engine_id:t,language:i})}}]);
//# sourceMappingURL=2566.04dedf78b2451f75.js.map