"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["9677"],{89969:function(e,t,r){r.a(e,(async function(e,a){try{r.r(t),r.d(t,{HaLabelSelector:function(){return v}});r(35748),r(95013);var i=r(69868),s=r(84922),n=r(11991),o=r(26846),l=r(73120),d=r(95403),u=e([d]);d=(u.then?(await u)():u)[0];let c,h,p,b=e=>e;class v extends s.WF{render(){var e;return this.selector.label.multiple?(0,s.qy)(c||(c=b`
        <ha-labels-picker
          no-add
          .hass=${0}
          .value=${0}
          .required=${0}
          .disabled=${0}
          .label=${0}
          @value-changed=${0}
        >
        </ha-labels-picker>
      `),this.hass,(0,o.e)(null!==(e=this.value)&&void 0!==e?e:[]),this.required,this.disabled,this.label,this._handleChange):(0,s.qy)(h||(h=b`
      <ha-label-picker
        no-add
        .hass=${0}
        .value=${0}
        .required=${0}
        .disabled=${0}
        .label=${0}
        @value-changed=${0}
      >
      </ha-label-picker>
    `),this.hass,this.value,this.required,this.disabled,this.label,this._handleChange)}_handleChange(e){let t=e.detail.value;this.value!==t&&((""===t||Array.isArray(t)&&0===t.length)&&!this.required&&(t=void 0),(0,l.r)(this,"value-changed",{value:t}))}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}v.styles=(0,s.AH)(p||(p=b`
    ha-labels-picker {
      display: block;
      width: 100%;
    }
  `)),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],v.prototype,"hass",void 0),(0,i.__decorate)([(0,n.MZ)()],v.prototype,"value",void 0),(0,i.__decorate)([(0,n.MZ)()],v.prototype,"name",void 0),(0,i.__decorate)([(0,n.MZ)()],v.prototype,"label",void 0),(0,i.__decorate)([(0,n.MZ)()],v.prototype,"placeholder",void 0),(0,i.__decorate)([(0,n.MZ)()],v.prototype,"helper",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],v.prototype,"selector",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],v.prototype,"disabled",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],v.prototype,"required",void 0),v=(0,i.__decorate)([(0,n.EM)("ha-selector-label")],v),a()}catch(c){a(c)}}))},47308:function(e,t,r){r.d(t,{N:function(){return s}});r(46852),r(99342),r(12977),r(5934);const a=e=>{let t=[];function r(r,a){e=a?r:Object.assign(Object.assign({},e),r);let i=t;for(let t=0;t<i.length;t++)i[t](e)}return{get state(){return e},action(t){function a(e){r(e,!1)}return function(){let r=[e];for(let e=0;e<arguments.length;e++)r.push(arguments[e]);let i=t.apply(this,r);if(null!=i)return i instanceof Promise?i.then(a):a(i)}},setState:r,clearState(){e=void 0},subscribe(e){return t.push(e),()=>{!function(e){let r=[];for(let a=0;a<t.length;a++)t[a]===e?e=null:r.push(t[a]);t=r}(e)}}}},i=(e,t,r,i,s={unsubGrace:!0})=>{if(e[t])return e[t];let n,o,l=0,d=a();const u=()=>{if(!r)throw new Error("Collection does not support refresh");return r(e).then((e=>d.setState(e,!0)))},c=()=>u().catch((t=>{if(e.connected)throw t})),h=()=>{o=void 0,n&&n.then((e=>{e()})),d.clearState(),e.removeEventListener("ready",u),e.removeEventListener("disconnected",p)},p=()=>{o&&(clearTimeout(o),h())};return e[t]={get state(){return d.state},refresh:u,subscribe(t){l++,1===l&&(()=>{if(void 0!==o)return clearTimeout(o),void(o=void 0);i&&(n=i(e,d)),r&&(e.addEventListener("ready",c),c()),e.addEventListener("disconnected",p)})();const a=d.subscribe(t);return void 0!==d.state&&setTimeout((()=>t(d.state)),0),()=>{a(),l--,l||(s.unsubGrace?o=setTimeout(h,5e3):h())}}},e[t]},s=(e,t,r,a,s)=>i(a,e,t,r).subscribe(s)}}]);
//# sourceMappingURL=9677.3bd8709061e38cbc.js.map