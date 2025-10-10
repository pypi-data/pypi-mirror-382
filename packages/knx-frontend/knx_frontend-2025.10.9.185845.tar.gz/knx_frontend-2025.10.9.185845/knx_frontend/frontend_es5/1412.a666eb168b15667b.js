"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["1412"],{13125:function(e,t,s){s.a(e,(async function(e,i){try{s.d(t,{T:function(){return l}});var a=s(96904),n=s(65940),r=e([a]);a=(r.then?(await r)():r)[0];const l=(e,t)=>{try{var s,i;return null!==(s=null===(i=d(t))||void 0===i?void 0:i.of(e))&&void 0!==s?s:e}catch(a){return e}},d=(0,n.A)((e=>new Intl.DisplayNames(e.language,{type:"language",fallback:"code"})));i()}catch(l){i(l)}}))},46102:function(e,t,s){s.a(e,(async function(e,t){try{s(35748),s(65315),s(84136),s(37089),s(95013);var i=s(69868),a=s(84922),n=s(11991),r=s(73120),l=s(20674),d=s(13125),o=s(85023),c=(s(25223),s(37207),e([d]));d=(c.then?(await c)():c)[0];let p,u,h,_,b=e=>e;const g="preferred",v="last_used";class y extends a.WF{get _default(){return this.includeLastUsed?v:g}render(){var e,t;if(!this._pipelines)return a.s6;const s=null!==(e=this.value)&&void 0!==e?e:this._default;return(0,a.qy)(p||(p=b`
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
        <ha-list-item .value=${0}>
          ${0}
        </ha-list-item>
        ${0}
      </ha-select>
    `),this.label||this.hass.localize("ui.components.pipeline-picker.pipeline"),s,this.required,this.disabled,this._changed,l.d,this.includeLastUsed?(0,a.qy)(u||(u=b`
              <ha-list-item .value=${0}>
                ${0}
              </ha-list-item>
            `),v,this.hass.localize("ui.components.pipeline-picker.last_used")):null,g,this.hass.localize("ui.components.pipeline-picker.preferred",{preferred:null===(t=this._pipelines.find((e=>e.id===this._preferredPipeline)))||void 0===t?void 0:t.name}),this._pipelines.map((e=>(0,a.qy)(h||(h=b`<ha-list-item .value=${0}>
              ${0}
              (${0})
            </ha-list-item>`),e.id,e.name,(0,d.T)(e.language,this.hass.locale)))))}firstUpdated(e){super.firstUpdated(e),(0,o.nx)(this.hass).then((e=>{this._pipelines=e.pipelines,this._preferredPipeline=e.preferred_pipeline}))}_changed(e){const t=e.target;!this.hass||""===t.value||t.value===this.value||void 0===this.value&&t.value===this._default||(this.value=t.value===this._default?void 0:t.value,(0,r.r)(this,"value-changed",{value:this.value}))}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.includeLastUsed=!1,this._preferredPipeline=null}}y.styles=(0,a.AH)(_||(_=b`
    ha-select {
      width: 100%;
    }
  `)),(0,i.__decorate)([(0,n.MZ)()],y.prototype,"value",void 0),(0,i.__decorate)([(0,n.MZ)()],y.prototype,"label",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],y.prototype,"hass",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],y.prototype,"disabled",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],y.prototype,"required",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],y.prototype,"includeLastUsed",void 0),(0,i.__decorate)([(0,n.wk)()],y.prototype,"_pipelines",void 0),(0,i.__decorate)([(0,n.wk)()],y.prototype,"_preferredPipeline",void 0),y=(0,i.__decorate)([(0,n.EM)("ha-assist-pipeline-picker")],y),t()}catch(p){t(p)}}))},22543:function(e,t,s){s.a(e,(async function(e,i){try{s.r(t),s.d(t,{HaAssistPipelineSelector:function(){return u}});s(35748),s(95013);var a=s(69868),n=s(84922),r=s(11991),l=s(46102),d=e([l]);l=(d.then?(await d)():d)[0];let o,c,p=e=>e;class u extends n.WF{render(){var e;return(0,n.qy)(o||(o=p`
      <ha-assist-pipeline-picker
        .hass=${0}
        .value=${0}
        .label=${0}
        .helper=${0}
        .disabled=${0}
        .required=${0}
        .includeLastUsed=${0}
      ></ha-assist-pipeline-picker>
    `),this.hass,this.value,this.label,this.helper,this.disabled,this.required,Boolean(null===(e=this.selector.assist_pipeline)||void 0===e?void 0:e.include_last_used))}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}u.styles=(0,n.AH)(c||(c=p`
    ha-conversation-agent-picker {
      width: 100%;
    }
  `)),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],u.prototype,"selector",void 0),(0,a.__decorate)([(0,r.MZ)()],u.prototype,"value",void 0),(0,a.__decorate)([(0,r.MZ)()],u.prototype,"label",void 0),(0,a.__decorate)([(0,r.MZ)()],u.prototype,"helper",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],u.prototype,"disabled",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],u.prototype,"required",void 0),u=(0,a.__decorate)([(0,r.EM)("ha-selector-assist_pipeline")],u),i()}catch(o){i(o)}}))},85023:function(e,t,s){s.d(t,{QC:function(){return i},ds:function(){return o},mp:function(){return r},nx:function(){return n},u6:function(){return l},vU:function(){return a},zn:function(){return d}});s(35748),s(12977),s(95013);const i=(e,t,s)=>"run-start"===t.type?e={init_options:s,stage:"ready",run:t.data,events:[t]}:e?((e="wake_word-start"===t.type?Object.assign(Object.assign({},e),{},{stage:"wake_word",wake_word:Object.assign(Object.assign({},t.data),{},{done:!1})}):"wake_word-end"===t.type?Object.assign(Object.assign({},e),{},{wake_word:Object.assign(Object.assign(Object.assign({},e.wake_word),t.data),{},{done:!0})}):"stt-start"===t.type?Object.assign(Object.assign({},e),{},{stage:"stt",stt:Object.assign(Object.assign({},t.data),{},{done:!1})}):"stt-end"===t.type?Object.assign(Object.assign({},e),{},{stt:Object.assign(Object.assign(Object.assign({},e.stt),t.data),{},{done:!0})}):"intent-start"===t.type?Object.assign(Object.assign({},e),{},{stage:"intent",intent:Object.assign(Object.assign({},t.data),{},{done:!1})}):"intent-end"===t.type?Object.assign(Object.assign({},e),{},{intent:Object.assign(Object.assign(Object.assign({},e.intent),t.data),{},{done:!0})}):"tts-start"===t.type?Object.assign(Object.assign({},e),{},{stage:"tts",tts:Object.assign(Object.assign({},t.data),{},{done:!1})}):"tts-end"===t.type?Object.assign(Object.assign({},e),{},{tts:Object.assign(Object.assign(Object.assign({},e.tts),t.data),{},{done:!0})}):"run-end"===t.type?Object.assign(Object.assign({},e),{},{stage:"done"}):"error"===t.type?Object.assign(Object.assign({},e),{},{stage:"error",error:t.data}):Object.assign({},e)).events=[...e.events,t],e):void console.warn("Received unexpected event before receiving session",t),a=(e,t,s)=>e.connection.subscribeMessage(t,Object.assign(Object.assign({},s),{},{type:"assist_pipeline/run"})),n=e=>e.callWS({type:"assist_pipeline/pipeline/list"}),r=(e,t)=>e.callWS({type:"assist_pipeline/pipeline/get",pipeline_id:t}),l=(e,t)=>e.callWS(Object.assign({type:"assist_pipeline/pipeline/create"},t)),d=(e,t,s)=>e.callWS(Object.assign({type:"assist_pipeline/pipeline/update",pipeline_id:t},s)),o=e=>e.callWS({type:"assist_pipeline/language/list"})}}]);
//# sourceMappingURL=1412.a666eb168b15667b.js.map