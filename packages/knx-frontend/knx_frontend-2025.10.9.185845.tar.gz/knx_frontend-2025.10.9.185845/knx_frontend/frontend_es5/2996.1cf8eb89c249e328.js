/*! For license information please see 2996.1cf8eb89c249e328.js.LICENSE.txt */
"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2996"],{72582:function(t,e,i){i.a(t,(async function(t,e){try{var n=i(69868),o=i(84922),s=i(11991),a=i(55),r=i(7556),c=i(93327),l=(i(81164),i(95635),t([c]));c=(l.then?(await l)():l)[0];let h,d,u,_,y=t=>t;class v extends o.WF{render(){var t,e;const i=this.icon||this.stateObj&&(null===(t=this.hass)||void 0===t||null===(t=t.entities[this.stateObj.entity_id])||void 0===t?void 0:t.icon)||(null===(e=this.stateObj)||void 0===e?void 0:e.attributes.icon);if(i)return(0,o.qy)(h||(h=y`<ha-icon .icon=${0}></ha-icon>`),i);if(!this.stateObj)return o.s6;if(!this.hass)return this._renderFallback();const n=(0,c.fq)(this.hass,this.stateObj,this.stateValue).then((t=>t?(0,o.qy)(d||(d=y`<ha-icon .icon=${0}></ha-icon>`),t):this._renderFallback()));return(0,o.qy)(u||(u=y`${0}`),(0,a.T)(n))}_renderFallback(){const t=(0,r.t)(this.stateObj);return(0,o.qy)(_||(_=y`
      <ha-svg-icon
        .path=${0}
      ></ha-svg-icon>
    `),c.l[t]||c.lW)}}(0,n.__decorate)([(0,s.MZ)({attribute:!1})],v.prototype,"hass",void 0),(0,n.__decorate)([(0,s.MZ)({attribute:!1})],v.prototype,"stateObj",void 0),(0,n.__decorate)([(0,s.MZ)({attribute:!1})],v.prototype,"stateValue",void 0),(0,n.__decorate)([(0,s.MZ)()],v.prototype,"icon",void 0),v=(0,n.__decorate)([(0,s.EM)("ha-state-icon")],v),e()}catch(h){e(h)}}))},88297:function(t,e,i){i.a(t,(async function(t,n){try{i.r(e),i.d(e,{KNXEntitiesView:function(){return j}});i(43114),i(35748),i(93225),i(65315),i(837),i(12791),i(37089),i(12977),i(5934),i(67579),i(88238),i(34536),i(16257),i(20152),i(44711),i(72108),i(77030),i(79566),i(95013),i(13484),i(81071),i(92714),i(55885);var o=i(69868),s=i(84922),a=i(11991),r=i(65940),c=i(92491),l=i(55204),h=(i(56730),i(81164),i(93672),i(72582)),d=(i(95635),i(68985)),u=i(90933),_=i(73120),y=i(47420),v=i(49432),f=i(92095),p=t([c,l,h]);[c,l,h]=p.then?(await p)():p;let b,$,g,C,m,x,k=t=>t;const w="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z",V="M11 7V9H13V7H11M14 17V15H13V11H10V13H11V15H10V17H14M22 12C22 17.5 17.5 22 12 22C6.5 22 2 17.5 2 12C2 6.5 6.5 2 12 2C17.5 2 22 6.5 22 12M20 12C20 7.58 16.42 4 12 4C7.58 4 4 7.58 4 12C4 16.42 7.58 20 12 20C16.42 20 20 16.42 20 12Z",H="M22.1 21.5L2.4 1.7L1.1 3L4.1 6C2.8 7.6 2 9.7 2 12C2 17.5 6.5 22 12 22C14.3 22 16.4 21.2 18 19.9L20.8 22.7L22.1 21.5M12 20C7.6 20 4 16.4 4 12C4 10.3 4.6 8.7 5.5 7.4L11 12.9V17H13V14.9L16.6 18.5C15.3 19.4 13.7 20 12 20M8.2 5L6.7 3.5C8.3 2.6 10.1 2 12 2C17.5 2 22 6.5 22 12C22 13.9 21.4 15.7 20.5 17.3L19 15.8C19.6 14.7 20 13.4 20 12C20 7.6 16.4 4 12 4C10.6 4 9.3 4.4 8.2 5M11 7H13V9H11V7Z",M="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",E="M14.06,9L15,9.94L5.92,19H5V18.08L14.06,9M17.66,3C17.41,3 17.15,3.1 16.96,3.29L15.13,5.12L18.88,8.87L20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18.17,3.09 17.92,3 17.66,3M14.06,6.19L3,17.25V21H6.75L17.81,9.94L14.06,6.19Z",L="M18 7C16.9 7 16 7.9 16 9V15C16 16.1 16.9 17 18 17H20C21.1 17 22 16.1 22 15V11H20V15H18V9H22V7H18M2 7V17H8V15H4V7H2M11 7C9.9 7 9 7.9 9 9V15C9 16.1 9.9 17 11 17H13C14.1 17 15 16.1 15 15V9C15 7.9 14.1 7 13 7H11M11 9H13V15H11V9Z",Z=new f.Q("knx-entities-view");class j extends s.WF{firstUpdated(){this._fetchEntities()}willUpdate(){const t=new URLSearchParams(u.G.location.search);this.filterDevice=t.get("device_id")}async _fetchEntities(){(0,v.ek)(this.hass).then((t=>{Z.debug(`Fetched ${t.length} entity entries.`),this.knx_entities=t.map((t=>{var e,i,n,o,s,a;const r=this.hass.states[t.entity_id],c=t.device_id?this.hass.devices[t.device_id]:void 0,l=null!==(e=t.area_id)&&void 0!==e?e:null==c?void 0:c.area_id,h=l?this.hass.areas[l]:void 0;return Object.assign(Object.assign({},t),{},{entityState:r,friendly_name:null!==(i=null!==(n=null!==(o=null==r?void 0:r.attributes.friendly_name)&&void 0!==o?o:t.name)&&void 0!==n?n:t.original_name)&&void 0!==i?i:"",device_name:null!==(s=null==c?void 0:c.name)&&void 0!==s?s:"",area_name:null!==(a=null==h?void 0:h.name)&&void 0!==a?a:"",disabled:!!t.disabled_by})}))})).catch((t=>{Z.error("getEntityEntries",t),(0,d.o)("/knx/error",{replace:!0,data:t})}))}render(){return this.hass&&this.knx_entities?(0,s.qy)($||($=k`
      <hass-tabs-subpage-data-table
        .hass=${0}
        .narrow=${0}
        .route=${0}
        .tabs=${0}
        .localizeFunc=${0}
        .columns=${0}
        .data=${0}
        .hasFab=${0}
        .searchLabel=${0}
        .clickable=${0}
        .filter=${0}
      >
        <ha-fab
          slot="fab"
          .label=${0}
          extended
          @click=${0}
        >
          <ha-svg-icon slot="icon" .path=${0}></ha-svg-icon>
        </ha-fab>
      </hass-tabs-subpage-data-table>
    `),this.hass,this.narrow,this.route,this.tabs,this.knx.localize,this._columns(this.hass.language),this.knx_entities,!0,this.hass.localize("ui.components.data-table.search"),!1,this.filterDevice,this.hass.localize("ui.common.add"),this._entityCreate,M):(0,s.qy)(b||(b=k` <hass-loading-screen></hass-loading-screen> `))}_entityCreate(){(0,d.o)("/knx/entities/create")}constructor(...t){super(...t),this.knx_entities=[],this.filterDevice=null,this._columns=(0,r.A)((t=>{const e="56px",i="224px";return{icon:{title:"",minWidth:e,maxWidth:e,type:"icon",template:t=>t.disabled?(0,s.qy)(g||(g=k`<ha-svg-icon
                slot="icon"
                label="Disabled entity"
                .path=${0}
                style="color: var(--disabled-text-color);"
              ></ha-svg-icon>`),H):(0,s.qy)(C||(C=k`
                <ha-state-icon
                  slot="item-icon"
                  .hass=${0}
                  .stateObj=${0}
                ></ha-state-icon>
              `),this.hass,t.entityState)},friendly_name:{showNarrow:!0,filterable:!0,sortable:!0,title:"Friendly Name",flex:2},entity_id:{filterable:!0,sortable:!0,title:"Entity ID",flex:1},device_name:{filterable:!0,sortable:!0,title:"Device",flex:1},device_id:{hidden:!0,title:"Device ID",filterable:!0,template:t=>{var e;return null!==(e=t.device_id)&&void 0!==e?e:""}},area_name:{title:"Area",sortable:!0,filterable:!0,flex:1},actions:{showNarrow:!0,title:"",minWidth:i,maxWidth:i,type:"icon-button",template:t=>(0,s.qy)(m||(m=k`
          <ha-icon-button
            .label=${0}
            .path=${0}
            .entityEntry=${0}
            @click=${0}
          ></ha-icon-button>
          <ha-icon-button
            .label=${0}
            .path=${0}
            .entityEntry=${0}
            @click=${0}
          ></ha-icon-button>
          <ha-icon-button
            .label=${0}
            .path=${0}
            .entityEntry=${0}
            @click=${0}
          ></ha-icon-button>
          <ha-icon-button
            .label=${0}
            .path=${0}
            .entityEntry=${0}
            @click=${0}
          ></ha-icon-button>
        `),"More info",V,t,this._entityMoreInfo,this.hass.localize("ui.common.edit"),E,t,this._entityEdit,this.knx.localize("entities_view_monitor_telegrams"),L,t,this._showEntityTelegrams,this.hass.localize("ui.common.delete"),w,t,this._entityDelete)}}})),this._entityEdit=t=>{t.stopPropagation();const e=t.target.entityEntry;(0,d.o)("/knx/entities/edit/"+e.entity_id)},this._entityMoreInfo=t=>{t.stopPropagation();const e=t.target.entityEntry;(0,_.r)(u.G.document.querySelector("home-assistant"),"hass-more-info",{entityId:e.entity_id})},this._showEntityTelegrams=async t=>{var e;t.stopPropagation();const i=null===(e=t.target)||void 0===e?void 0:e.entityEntry;if(!i)return Z.error("No entity entry found in event target"),void(0,d.o)("/knx/group_monitor");try{const t=(await(0,v.wE)(this.hass,i.entity_id)).data.knx,e=Object.values(t).flatMap((t=>{if("object"!=typeof t||null===t)return[];const{write:e,state:i,passive:n}=t;return[e,i,...Array.isArray(n)?n:[]]})).filter((t=>Boolean(t))),n=[...new Set(e)];if(n.length>0){const t=n.join(",");(0,d.o)(`/knx/group_monitor?destination=${encodeURIComponent(t)}`)}else Z.warn("No group addresses found for entity",i.entity_id),(0,d.o)("/knx/group_monitor")}catch(n){Z.error("Failed to load entity configuration for monitor",i.entity_id,n),(0,d.o)("/knx/group_monitor")}},this._entityDelete=t=>{t.stopPropagation();const e=t.target.entityEntry;(0,y.dk)(this,{text:`${this.hass.localize("ui.common.delete")} ${e.entity_id}?`}).then((t=>{t&&(0,v.$b)(this.hass,e.entity_id).then((()=>{Z.debug("entity deleted",e.entity_id),this._fetchEntities()})).catch((t=>{(0,y.K$)(this,{title:"Deletion failed",text:t})}))}))}}}j.styles=(0,s.AH)(x||(x=k`
    hass-loading-screen {
      --app-header-background-color: var(--sidebar-background-color);
      --app-header-text-color: var(--sidebar-text-color);
    }
  `)),(0,o.__decorate)([(0,a.MZ)({type:Object})],j.prototype,"hass",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],j.prototype,"knx",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean,reflect:!0})],j.prototype,"narrow",void 0),(0,o.__decorate)([(0,a.MZ)({type:Object})],j.prototype,"route",void 0),(0,o.__decorate)([(0,a.MZ)({type:Array,reflect:!1})],j.prototype,"tabs",void 0),(0,o.__decorate)([(0,a.wk)()],j.prototype,"knx_entities",void 0),(0,o.__decorate)([(0,a.wk)()],j.prototype,"filterDevice",void 0),j=(0,o.__decorate)([(0,a.EM)("knx-entities-view")],j),n()}catch(b){n(b)}}))},36838:function(t,e,i){var n=i(30354);t.exports=function(t,e,i){for(var o=0,s=arguments.length>2?i:n(e),a=new t(s);s>o;)a[o]=e[o++];return a}},51017:function(t,e,i){var n=i(16732),o=i(42244),s=i(48579),a=i(77977),r=i(67309),c=i(30354),l=i(83124),h=i(36838),d=Array,u=o([].push);t.exports=function(t,e,i,o){for(var _,y,v,f=a(t),p=s(f),b=n(e,i),$=l(null),g=c(p),C=0;g>C;C++)v=p[C],(y=r(b(v,C,f)))in $?u($[y],v):$[y]=[v];if(o&&(_=o(f))!==d)for(y in $)$[y]=h(_,$[y]);return $}},89180:function(t,e,i){var n=i(6764),o=Math.floor,s=function(t,e){var i=t.length;if(i<8)for(var a,r,c=1;c<i;){for(r=c,a=t[c];r&&e(t[r-1],a)>0;)t[r]=t[--r];r!==c++&&(t[r]=a)}else for(var l=o(i/2),h=s(n(t,0,l),e),d=s(n(t,l),e),u=h.length,_=d.length,y=0,v=0;y<u||v<_;)t[y+v]=y<u&&v<_?e(h[y],d[v])<=0?h[y++]:d[v++]:y<u?h[y++]:d[v++];return t};t.exports=s},78609:function(t,e,i){var n=i(94971).match(/firefox\/(\d+)/i);t.exports=!!n&&+n[1]},69615:function(t,e,i){var n=i(94971);t.exports=/MSIE|Trident/.test(n)},33651:function(t,e,i){var n=i(94971).match(/AppleWebKit\/(\d+)\./);t.exports=!!n&&+n[1]},75513:function(t,e,i){var n=i(36196),o=i(50941);t.exports=function(t){if(o){try{return n.process.getBuiltinModule(t)}catch(e){}try{return Function('return require("'+t+'")')()}catch(e){}}}},75846:function(t,e,i){var n=i(87642),o=i(51017),s=i(93017);n({target:"Array",proto:!0},{group:function(t){return o(this,t,arguments.length>1?arguments[1]:void 0)}}),s("group")},55:function(t,e,i){i.d(e,{T:function(){return u}});i(35748),i(65315),i(84136),i(5934),i(95013);var n=i(11681),o=i(67851),s=i(40594);i(32203),i(79392),i(46852);class a{disconnect(){this.G=void 0}reconnect(t){this.G=t}deref(){return this.G}constructor(t){this.G=t}}class r{get(){return this.Y}pause(){var t;null!==(t=this.Y)&&void 0!==t||(this.Y=new Promise((t=>this.Z=t)))}resume(){var t;null!==(t=this.Z)&&void 0!==t&&t.call(this),this.Y=this.Z=void 0}constructor(){this.Y=void 0,this.Z=void 0}}var c=i(64363);const l=t=>!(0,o.sO)(t)&&"function"==typeof t.then,h=1073741823;class d extends s.Kq{render(...t){var e;return null!==(e=t.find((t=>!l(t))))&&void 0!==e?e:n.c0}update(t,e){const i=this._$Cbt;let o=i.length;this._$Cbt=e;const s=this._$CK,a=this._$CX;this.isConnected||this.disconnected();for(let n=0;n<e.length&&!(n>this._$Cwt);n++){const t=e[n];if(!l(t))return this._$Cwt=n,t;n<o&&t===i[n]||(this._$Cwt=h,o=0,Promise.resolve(t).then((async e=>{for(;a.get();)await a.get();const i=s.deref();if(void 0!==i){const n=i._$Cbt.indexOf(t);n>-1&&n<i._$Cwt&&(i._$Cwt=n,i.setValue(e))}})))}return n.c0}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}constructor(){super(...arguments),this._$Cwt=h,this._$Cbt=[],this._$CK=new a(this),this._$CX=new r}}const u=(0,c.u$)(d)}}]);
//# sourceMappingURL=2996.1cf8eb89c249e328.js.map