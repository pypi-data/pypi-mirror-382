"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["364"],{51079:function(e,t,a){a.r(t),a.d(t,{HaFormExpandable:function(){return d}});a(35748),a(12977),a(47849),a(95013);var o=a(69868),i=a(84922),s=a(11991);a(75518),a(99741);let n,c,l,h,r,p=e=>e;class d extends i.WF{_renderDescription(){var e;const t=null===(e=this.computeHelper)||void 0===e?void 0:e.call(this,this.schema);return t?(0,i.qy)(n||(n=p`<p>${0}</p>`),t):i.s6}render(){var e,t,a;return(0,i.qy)(c||(c=p`
      <ha-expansion-panel outlined .expanded=${0}>
        ${0}
        <div
          slot="header"
          role="heading"
          aria-level=${0}
        >
          ${0}
        </div>
        <div class="content">
          ${0}
          <ha-form
            .hass=${0}
            .data=${0}
            .schema=${0}
            .disabled=${0}
            .computeLabel=${0}
            .computeHelper=${0}
            .localizeValue=${0}
          ></ha-form>
        </div>
      </ha-expansion-panel>
    `),Boolean(this.schema.expanded),this.schema.icon?(0,i.qy)(l||(l=p`
              <ha-icon slot="leading-icon" .icon=${0}></ha-icon>
            `),this.schema.icon):this.schema.iconPath?(0,i.qy)(h||(h=p`
                <ha-svg-icon
                  slot="leading-icon"
                  .path=${0}
                ></ha-svg-icon>
              `),this.schema.iconPath):i.s6,null!==(e=null===(t=this.schema.headingLevel)||void 0===t?void 0:t.toString())&&void 0!==e?e:"3",this.schema.title||(null===(a=this.computeLabel)||void 0===a?void 0:a.call(this,this.schema)),this._renderDescription(),this.hass,this.data,this.schema.schema,this.disabled,this._computeLabel,this._computeHelper,this.localizeValue)}constructor(...e){super(...e),this.disabled=!1,this._computeLabel=(e,t,a)=>this.computeLabel?this.computeLabel(e,t,Object.assign(Object.assign({},a),{},{path:[...(null==a?void 0:a.path)||[],this.schema.name]})):this.computeLabel,this._computeHelper=(e,t)=>this.computeHelper?this.computeHelper(e,Object.assign(Object.assign({},t),{},{path:[...(null==t?void 0:t.path)||[],this.schema.name]})):this.computeHelper}}d.styles=(0,i.AH)(r||(r=p`
    :host {
      display: flex !important;
      flex-direction: column;
    }
    :host ha-form {
      display: block;
    }
    .content {
      padding: 12px;
    }
    .content p {
      margin: 0 0 24px;
    }
    ha-expansion-panel {
      display: block;
      --expansion-panel-content-padding: 0;
      border-radius: 6px;
      --ha-card-border-radius: 6px;
    }
    ha-svg-icon,
    ha-icon {
      color: var(--secondary-text-color);
    }
  `)),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"data",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"schema",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],d.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"computeLabel",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"computeHelper",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"localizeValue",void 0),d=(0,o.__decorate)([(0,s.EM)("ha-form-expandable")],d)}}]);
//# sourceMappingURL=364.2d199105c6e02474.js.map