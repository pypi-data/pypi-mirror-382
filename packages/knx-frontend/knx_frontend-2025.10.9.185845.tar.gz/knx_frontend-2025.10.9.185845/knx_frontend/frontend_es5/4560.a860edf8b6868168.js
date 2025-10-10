"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["4560"],{50275:function(e,t,s){s.r(t),s.d(t,{HaBackupLocationSelector:function(){return f}});s(35748),s(95013);var a=s(69868),o=s(84922),r=s(11991),i=(s(79827),s(35058),s(65315),s(837),s(37089),s(5934),s(65940)),u=s(10763),n=s(73120),h=s(20674),l=s(90963),p=function(e){return e.BIND="bind",e.CIFS="cifs",e.NFS="nfs",e}({}),c=function(e){return e.BACKUP="backup",e.MEDIA="media",e.SHARE="share",e}({});s(23749),s(25223),s(37207);let d,_,m,v,A,y=e=>e;const M="/backup";class b extends o.WF{firstUpdated(){this._getMounts()}render(){if(this._error)return(0,o.qy)(d||(d=y`<ha-alert alert-type="error">${0}</ha-alert>`),this._error);if(!this._mounts)return o.s6;const e=(0,o.qy)(_||(_=y`<ha-list-item
      graphic="icon"
      .value=${0}
    >
      <span>
        ${0}
      </span>
      <ha-svg-icon slot="graphic" .path=${0}></ha-svg-icon>
    </ha-list-item>`),M,this.hass.localize("ui.components.mount-picker.use_datadisk")||"Use data disk for backup","M6,2H18A2,2 0 0,1 20,4V20A2,2 0 0,1 18,22H6A2,2 0 0,1 4,20V4A2,2 0 0,1 6,2M12,4A6,6 0 0,0 6,10C6,13.31 8.69,16 12.1,16L11.22,13.77C10.95,13.29 11.11,12.68 11.59,12.4L12.45,11.9C12.93,11.63 13.54,11.79 13.82,12.27L15.74,14.69C17.12,13.59 18,11.9 18,10A6,6 0 0,0 12,4M12,9A1,1 0 0,1 13,10A1,1 0 0,1 12,11A1,1 0 0,1 11,10A1,1 0 0,1 12,9M7,18A1,1 0 0,0 6,19A1,1 0 0,0 7,20A1,1 0 0,0 8,19A1,1 0 0,0 7,18M12.09,13.27L14.58,19.58L17.17,18.08L12.95,12.77L12.09,13.27Z");return(0,o.qy)(m||(m=y`
      <ha-select
        .label=${0}
        .value=${0}
        .required=${0}
        .disabled=${0}
        .helper=${0}
        @selected=${0}
        @closed=${0}
        fixedMenuPosition
        naturalMenuWidth
      >
        ${0}
        ${0}
        ${0}
      </ha-select>
    `),void 0===this.label&&this.hass?this.hass.localize("ui.components.mount-picker.mount"):this.label,this._value,this.required,this.disabled,this.helper,this._mountChanged,h.d,this.usage!==c.BACKUP||this._mounts.default_backup_mount&&this._mounts.default_backup_mount!==M?o.s6:e,this._filterMounts(this._mounts,this.usage).map((e=>(0,o.qy)(v||(v=y`<ha-list-item twoline graphic="icon" .value=${0}>
              <span>${0}</span>
              <span slot="secondary"
                >${0}${0}${0}</span
              >
              <ha-svg-icon
                slot="graphic"
                .path=${0}
              ></ha-svg-icon>
            </ha-list-item>`),e.name,e.name,e.server,e.port?`:${e.port}`:o.s6,e.type===p.NFS?e.path:`:${e.share}`,e.usage===c.MEDIA?"M19 3H5C3.89 3 3 3.89 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.89 20.1 3 19 3M10 16V8L15 12":e.usage===c.SHARE?"M10,4H4C2.89,4 2,4.89 2,6V18A2,2 0 0,0 4,20H20A2,2 0 0,0 22,18V8C22,6.89 21.1,6 20,6H12L10,4Z":"M12,3A9,9 0 0,0 3,12H0L4,16L8,12H5A7,7 0 0,1 12,5A7,7 0 0,1 19,12A7,7 0 0,1 12,19C10.5,19 9.09,18.5 7.94,17.7L6.5,19.14C8.04,20.3 9.94,21 12,21A9,9 0 0,0 21,12A9,9 0 0,0 12,3M14,12A2,2 0 0,0 12,10A2,2 0 0,0 10,12A2,2 0 0,0 12,14A2,2 0 0,0 14,12Z"))),this.usage===c.BACKUP&&this._mounts.default_backup_mount?e:o.s6)}async _getMounts(){try{(0,u.x)(this.hass,"hassio")?(this._mounts=await(async e=>e.callWS({type:"supervisor/api",endpoint:"/mounts",method:"get",timeout:null}))(this.hass),this.usage!==c.BACKUP||this.value||(this.value=this._mounts.default_backup_mount||M)):this._error=this.hass.localize("ui.components.mount-picker.error.no_supervisor")}catch(e){this._error=this.hass.localize("ui.components.mount-picker.error.fetch_mounts")}}get _value(){return this.value||""}_mountChanged(e){e.stopPropagation();const t=e.target.value;t!==this._value&&this._setValue(t)}_setValue(e){this.value=e,setTimeout((()=>{(0,n.r)(this,"value-changed",{value:e}),(0,n.r)(this,"change")}),0)}static get styles(){return[(0,o.AH)(A||(A=y`
        ha-select {
          width: 100%;
        }
      `))]}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this._filterMounts=(0,i.A)(((e,t)=>{let s=e.mounts.filter((e=>[p.CIFS,p.NFS].includes(e.type)));return t&&(s=e.mounts.filter((e=>e.usage===t))),s.sort(((t,s)=>t.name===e.default_backup_mount?-1:s.name===e.default_backup_mount?1:(0,l.SH)(t.name,s.name,this.hass.locale.language)))}))}}(0,a.__decorate)([(0,r.MZ)()],b.prototype,"label",void 0),(0,a.__decorate)([(0,r.MZ)()],b.prototype,"value",void 0),(0,a.__decorate)([(0,r.MZ)()],b.prototype,"helper",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],b.prototype,"disabled",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],b.prototype,"required",void 0),(0,a.__decorate)([(0,r.MZ)()],b.prototype,"usage",void 0),(0,a.__decorate)([(0,r.wk)()],b.prototype,"_mounts",void 0),(0,a.__decorate)([(0,r.wk)()],b.prototype,"_error",void 0),b=(0,a.__decorate)([(0,r.EM)("ha-mount-picker")],b);let g,k,$=e=>e;class f extends o.WF{render(){return(0,o.qy)(g||(g=$`<ha-mount-picker
      .hass=${0}
      .value=${0}
      .label=${0}
      .helper=${0}
      .disabled=${0}
      .required=${0}
      usage="backup"
    ></ha-mount-picker>`),this.hass,this.value,this.label,this.helper,this.disabled,this.required)}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}f.styles=(0,o.AH)(k||(k=$`
    ha-mount-picker {
      width: 100%;
    }
  `)),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],f.prototype,"hass",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],f.prototype,"selector",void 0),(0,a.__decorate)([(0,r.MZ)()],f.prototype,"value",void 0),(0,a.__decorate)([(0,r.MZ)()],f.prototype,"label",void 0),(0,a.__decorate)([(0,r.MZ)()],f.prototype,"helper",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],f.prototype,"disabled",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],f.prototype,"required",void 0),f=(0,a.__decorate)([(0,r.EM)("ha-selector-backup_location")],f)}}]);
//# sourceMappingURL=4560.a860edf8b6868168.js.map