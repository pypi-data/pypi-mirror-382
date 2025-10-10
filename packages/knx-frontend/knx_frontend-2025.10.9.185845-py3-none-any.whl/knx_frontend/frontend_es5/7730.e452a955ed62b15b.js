/*! For license information please see 7730.e452a955ed62b15b.js.LICENSE.txt */
"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["7730"],{35881:function(e,t,o){o.a(e,(async function(e,r){try{o.r(t),o.d(t,{HaIconOverflowMenu:function(){return _}});o(35748),o(65315),o(37089),o(95013);var i=o(69868),n=o(84922),a=o(11991),s=o(75907),l=o(83566),d=(o(61647),o(93672),o(95635),o(89652)),c=(o(70154),o(90666),e([d]));d=(c.then?(await c)():c)[0];let m,h,p,u,y,g,v,f,b=e=>e;const x="M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z";class _ extends n.WF{render(){return(0,n.qy)(m||(m=b`
      ${0}
    `),this.narrow?(0,n.qy)(h||(h=b` <!-- Collapsed representation for small screens -->
            <ha-md-button-menu
              @click=${0}
              positioning="popover"
            >
              <ha-icon-button
                .label=${0}
                .path=${0}
                slot="trigger"
              ></ha-icon-button>

              ${0}
            </ha-md-button-menu>`),this._handleIconOverflowMenuOpened,this.hass.localize("ui.common.overflow_menu"),x,this.items.map((e=>e.divider?(0,n.qy)(p||(p=b`<ha-md-divider
                      role="separator"
                      tabindex="-1"
                    ></ha-md-divider>`)):(0,n.qy)(u||(u=b`<ha-md-menu-item
                      ?disabled=${0}
                      .clickAction=${0}
                      class=${0}
                    >
                      <ha-svg-icon
                        slot="start"
                        class=${0}
                        .path=${0}
                      ></ha-svg-icon>
                      ${0}
                    </ha-md-menu-item> `),e.disabled,e.action,(0,s.H)({warning:Boolean(e.warning)}),(0,s.H)({warning:Boolean(e.warning)}),e.path,e.label)))):(0,n.qy)(y||(y=b`
            <!-- Icon representation for big screens -->
            ${0}
          `),this.items.map((e=>{var t;return e.narrowOnly?n.s6:e.divider?(0,n.qy)(g||(g=b`<div role="separator"></div>`)):(0,n.qy)(v||(v=b`<ha-tooltip
                        .disabled=${0}
                        .for="icon-button-${0}"
                        >${0} </ha-tooltip
                      ><ha-icon-button
                        .id="icon-button-${0}"
                        @click=${0}
                        .label=${0}
                        .path=${0}
                        ?disabled=${0}
                      ></ha-icon-button> `),!e.tooltip,e.label,null!==(t=e.tooltip)&&void 0!==t?t:"",e.label,e.action,e.label,e.path,e.disabled)}))))}_handleIconOverflowMenuOpened(e){e.stopPropagation()}static get styles(){return[l.RF,(0,n.AH)(f||(f=b`
        :host {
          display: flex;
          justify-content: flex-end;
        }
        div[role="separator"] {
          border-right: 1px solid var(--divider-color);
          width: 1px;
        }
      `))]}constructor(...e){super(...e),this.items=[],this.narrow=!1}}(0,i.__decorate)([(0,a.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,i.__decorate)([(0,a.MZ)({type:Array})],_.prototype,"items",void 0),(0,i.__decorate)([(0,a.MZ)({type:Boolean})],_.prototype,"narrow",void 0),_=(0,i.__decorate)([(0,a.EM)("ha-icon-overflow-menu")],_),r()}catch(m){r(m)}}))},61647:function(e,t,o){o(35748),o(95013);var r=o(69868),i=o(84922),n=o(11991),a=o(73120),s=(o(9974),o(5673)),l=o(89591),d=o(18396);let c;class m extends s.W1{connectedCallback(){super.connectedCallback(),this.addEventListener("close-menu",this._handleCloseMenu)}_handleCloseMenu(e){var t,o;e.detail.reason.kind===d.fi.KEYDOWN&&e.detail.reason.key===d.NV.ESCAPE||null===(t=(o=e.detail.initiator).clickAction)||void 0===t||t.call(o,e.detail.initiator)}}m.styles=[l.R,(0,i.AH)(c||(c=(e=>e)`
      :host {
        --md-sys-color-surface-container: var(--card-background-color);
      }
    `))],m=(0,r.__decorate)([(0,n.EM)("ha-md-menu")],m);let h,p,u=e=>e;class y extends i.WF{get items(){return this._menu.items}focus(){var e;this._menu.open?this._menu.focus():null===(e=this._triggerButton)||void 0===e||e.focus()}render(){return(0,i.qy)(h||(h=u`
      <div @click=${0}>
        <slot name="trigger" @slotchange=${0}></slot>
      </div>
      <ha-md-menu
        .quick=${0}
        .positioning=${0}
        .hasOverflow=${0}
        .anchorCorner=${0}
        .menuCorner=${0}
        @opening=${0}
        @closing=${0}
      >
        <slot></slot>
      </ha-md-menu>
    `),this._handleClick,this._setTriggerAria,this.quick,this.positioning,this.hasOverflow,this.anchorCorner,this.menuCorner,this._handleOpening,this._handleClosing)}_handleOpening(){(0,a.r)(this,"opening",void 0,{composed:!1})}_handleClosing(){(0,a.r)(this,"closing",void 0,{composed:!1})}_handleClick(){this.disabled||(this._menu.anchorElement=this,this._menu.open?this._menu.close():this._menu.show())}get _triggerButton(){return this.querySelector('ha-icon-button[slot="trigger"], ha-button[slot="trigger"], ha-assist-chip[slot="trigger"]')}_setTriggerAria(){this._triggerButton&&(this._triggerButton.ariaHasPopup="menu")}constructor(...e){super(...e),this.disabled=!1,this.anchorCorner="end-start",this.menuCorner="start-start",this.hasOverflow=!1,this.quick=!1}}y.styles=(0,i.AH)(p||(p=u`
    :host {
      display: inline-block;
      position: relative;
    }
    ::slotted([disabled]) {
      color: var(--disabled-text-color);
    }
  `)),(0,r.__decorate)([(0,n.MZ)({type:Boolean})],y.prototype,"disabled",void 0),(0,r.__decorate)([(0,n.MZ)()],y.prototype,"positioning",void 0),(0,r.__decorate)([(0,n.MZ)({attribute:"anchor-corner"})],y.prototype,"anchorCorner",void 0),(0,r.__decorate)([(0,n.MZ)({attribute:"menu-corner"})],y.prototype,"menuCorner",void 0),(0,r.__decorate)([(0,n.MZ)({type:Boolean,attribute:"has-overflow"})],y.prototype,"hasOverflow",void 0),(0,r.__decorate)([(0,n.MZ)({type:Boolean})],y.prototype,"quick",void 0),(0,r.__decorate)([(0,n.P)("ha-md-menu",!0)],y.prototype,"_menu",void 0),y=(0,r.__decorate)([(0,n.EM)("ha-md-button-menu")],y)},90666:function(e,t,o){var r=o(69868),i=o(61320),n=o(41715),a=o(84922),s=o(11991);let l;class d extends i.c{}d.styles=[n.R,(0,a.AH)(l||(l=(e=>e)`
      :host {
        --md-divider-color: var(--divider-color);
      }
    `))],d=(0,r.__decorate)([(0,s.EM)("ha-md-divider")],d)},70154:function(e,t,o){var r=o(69868),i=o(45369),n=o(20808),a=o(84922),s=o(11991);let l;class d extends i.K{}d.styles=[n.R,(0,a.AH)(l||(l=(e=>e)`
      :host {
        --ha-icon-display: block;
        --md-sys-color-primary: var(--primary-text-color);
        --md-sys-color-on-primary: var(--primary-text-color);
        --md-sys-color-secondary: var(--secondary-text-color);
        --md-sys-color-surface: var(--card-background-color);
        --md-sys-color-on-surface: var(--primary-text-color);
        --md-sys-color-on-surface-variant: var(--secondary-text-color);
        --md-sys-color-secondary-container: rgba(
          var(--rgb-primary-color),
          0.15
        );
        --md-sys-color-on-secondary-container: var(--text-primary-color);
        --mdc-icon-size: 16px;

        --md-sys-color-on-primary-container: var(--primary-text-color);
        --md-sys-color-on-secondary-container: var(--primary-text-color);
        --md-menu-item-label-text-font: Roboto, sans-serif;
      }
      :host(.warning) {
        --md-menu-item-label-text-color: var(--error-color);
        --md-menu-item-leading-icon-color: var(--error-color);
      }
      ::slotted([slot="headline"]) {
        text-wrap: nowrap;
      }
    `))],(0,r.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"clickAction",void 0),d=(0,r.__decorate)([(0,s.EM)("ha-md-menu-item")],d)},89652:function(e,t,o){o.a(e,(async function(e,t){try{o(35748),o(95013);var r=o(69868),i=o(28784),n=o(84922),a=o(11991),s=e([i]);i=(s.then?(await s)():s)[0];let l,d=e=>e;class c extends i.A{static get styles(){return[i.A.styles,(0,n.AH)(l||(l=d`
        :host {
          --wa-tooltip-background-color: var(--secondary-background-color);
          --wa-tooltip-color: var(--primary-text-color);
          --wa-tooltip-font-family: var(
            --ha-tooltip-font-family,
            var(--ha-font-family-body)
          );
          --wa-tooltip-font-size: var(
            --ha-tooltip-font-size,
            var(--ha-font-size-s)
          );
          --wa-tooltip-font-weight: var(
            --ha-tooltip-font-weight,
            var(--ha-font-weight-normal)
          );
          --wa-tooltip-line-height: var(
            --ha-tooltip-line-height,
            var(--ha-line-height-condensed)
          );
          --wa-tooltip-padding: 8px;
          --wa-tooltip-border-radius: var(--ha-tooltip-border-radius, 4px);
          --wa-tooltip-arrow-size: var(--ha-tooltip-arrow-size, 8px);
          --wa-z-index-tooltip: var(--ha-tooltip-z-index, 1000);
        }
      `))]}constructor(...e){super(...e),this.showDelay=150,this.hideDelay=400}}(0,r.__decorate)([(0,a.MZ)({attribute:"show-delay",type:Number})],c.prototype,"showDelay",void 0),(0,r.__decorate)([(0,a.MZ)({attribute:"hide-delay",type:Number})],c.prototype,"hideDelay",void 0),c=(0,r.__decorate)([(0,a.EM)("ha-tooltip")],c),t()}catch(l){t(l)}}))},41715:function(e,t,o){o.d(t,{R:function(){return i}});let r;const i=(0,o(84922).AH)(r||(r=(e=>e)`:host{box-sizing:border-box;color:var(--md-divider-color, var(--md-sys-color-outline-variant, #cac4d0));display:flex;height:var(--md-divider-thickness, 1px);width:100%}:host([inset]),:host([inset-start]){padding-inline-start:16px}:host([inset]),:host([inset-end]){padding-inline-end:16px}:host::before{background:currentColor;content:"";height:100%;width:100%}@media(forced-colors: active){:host::before{background:CanvasText}}
`))},61320:function(e,t,o){o.d(t,{c:function(){return a}});o(35748),o(95013);var r=o(69868),i=o(84922),n=o(11991);class a extends i.WF{constructor(){super(...arguments),this.inset=!1,this.insetStart=!1,this.insetEnd=!1}}(0,r.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],a.prototype,"inset",void 0),(0,r.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0,attribute:"inset-start"})],a.prototype,"insetStart",void 0),(0,r.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0,attribute:"inset-end"})],a.prototype,"insetEnd",void 0)},48521:function(e,t,o){o.d(t,{X:function(){return i}});o(37216),o(99342),o(65315),o(22416),o(39118);var r=o(18396);class i{get typeaheadText(){if(null!==this.internalTypeaheadText)return this.internalTypeaheadText;const e=this.getHeadlineElements(),t=[];return e.forEach((e=>{e.textContent&&e.textContent.trim()&&t.push(e.textContent.trim())})),0===t.length&&this.getDefaultElements().forEach((e=>{e.textContent&&e.textContent.trim()&&t.push(e.textContent.trim())})),0===t.length&&this.getSupportingTextElements().forEach((e=>{e.textContent&&e.textContent.trim()&&t.push(e.textContent.trim())})),t.join(" ")}get tagName(){switch(this.host.type){case"link":return"a";case"button":return"button";default:return"li"}}get role(){return"option"===this.host.type?"option":"menuitem"}hostConnected(){this.host.toggleAttribute("md-menu-item",!0)}hostUpdate(){this.host.href&&(this.host.type="link")}setTypeaheadText(e){this.internalTypeaheadText=e}constructor(e,t){this.host=e,this.internalTypeaheadText=null,this.onClick=()=>{this.host.keepOpen||this.host.dispatchEvent((0,r.xr)(this.host,{kind:r.fi.CLICK_SELECTION}))},this.onKeydown=e=>{if(this.host.href&&"Enter"===e.code){const e=this.getInteractiveElement();e instanceof HTMLAnchorElement&&e.click()}if(e.defaultPrevented)return;const t=e.code;this.host.keepOpen&&"Escape"!==t||(0,r.Rb)(t)&&(e.preventDefault(),this.host.dispatchEvent((0,r.xr)(this.host,{kind:r.fi.KEYDOWN,key:t})))},this.getHeadlineElements=t.getHeadlineElements,this.getSupportingTextElements=t.getSupportingTextElements,this.getDefaultElements=t.getDefaultElements,this.getInteractiveElement=t.getInteractiveElement,this.host.addController(this)}}},20808:function(e,t,o){o.d(t,{R:function(){return i}});let r;const i=(0,o(84922).AH)(r||(r=(e=>e)`:host{display:flex;--md-ripple-hover-color: var(--md-menu-item-hover-state-layer-color, var(--md-sys-color-on-surface, #1d1b20));--md-ripple-hover-opacity: var(--md-menu-item-hover-state-layer-opacity, 0.08);--md-ripple-pressed-color: var(--md-menu-item-pressed-state-layer-color, var(--md-sys-color-on-surface, #1d1b20));--md-ripple-pressed-opacity: var(--md-menu-item-pressed-state-layer-opacity, 0.12)}:host([disabled]){opacity:var(--md-menu-item-disabled-opacity, 0.3);pointer-events:none}md-focus-ring{z-index:1;--md-focus-ring-shape: 8px}a,button,li{background:none;border:none;padding:0;margin:0;text-align:unset;text-decoration:none}.list-item{border-radius:inherit;display:flex;flex:1;max-width:inherit;min-width:inherit;outline:none;-webkit-tap-highlight-color:rgba(0,0,0,0)}.list-item:not(.disabled){cursor:pointer}[slot=container]{pointer-events:none}md-ripple{border-radius:inherit}md-item{border-radius:inherit;flex:1;color:var(--md-menu-item-label-text-color, var(--md-sys-color-on-surface, #1d1b20));font-family:var(--md-menu-item-label-text-font, var(--md-sys-typescale-body-large-font, var(--md-ref-typeface-plain, Roboto)));font-size:var(--md-menu-item-label-text-size, var(--md-sys-typescale-body-large-size, 1rem));line-height:var(--md-menu-item-label-text-line-height, var(--md-sys-typescale-body-large-line-height, 1.5rem));font-weight:var(--md-menu-item-label-text-weight, var(--md-sys-typescale-body-large-weight, var(--md-ref-typeface-weight-regular, 400)));min-height:var(--md-menu-item-one-line-container-height, 56px);padding-top:var(--md-menu-item-top-space, 12px);padding-bottom:var(--md-menu-item-bottom-space, 12px);padding-inline-start:var(--md-menu-item-leading-space, 16px);padding-inline-end:var(--md-menu-item-trailing-space, 16px)}md-item[multiline]{min-height:var(--md-menu-item-two-line-container-height, 72px)}[slot=supporting-text]{color:var(--md-menu-item-supporting-text-color, var(--md-sys-color-on-surface-variant, #49454f));font-family:var(--md-menu-item-supporting-text-font, var(--md-sys-typescale-body-medium-font, var(--md-ref-typeface-plain, Roboto)));font-size:var(--md-menu-item-supporting-text-size, var(--md-sys-typescale-body-medium-size, 0.875rem));line-height:var(--md-menu-item-supporting-text-line-height, var(--md-sys-typescale-body-medium-line-height, 1.25rem));font-weight:var(--md-menu-item-supporting-text-weight, var(--md-sys-typescale-body-medium-weight, var(--md-ref-typeface-weight-regular, 400)))}[slot=trailing-supporting-text]{color:var(--md-menu-item-trailing-supporting-text-color, var(--md-sys-color-on-surface-variant, #49454f));font-family:var(--md-menu-item-trailing-supporting-text-font, var(--md-sys-typescale-label-small-font, var(--md-ref-typeface-plain, Roboto)));font-size:var(--md-menu-item-trailing-supporting-text-size, var(--md-sys-typescale-label-small-size, 0.6875rem));line-height:var(--md-menu-item-trailing-supporting-text-line-height, var(--md-sys-typescale-label-small-line-height, 1rem));font-weight:var(--md-menu-item-trailing-supporting-text-weight, var(--md-sys-typescale-label-small-weight, var(--md-ref-typeface-weight-medium, 500)))}:is([slot=start],[slot=end])::slotted(*){fill:currentColor}[slot=start]{color:var(--md-menu-item-leading-icon-color, var(--md-sys-color-on-surface-variant, #49454f))}[slot=end]{color:var(--md-menu-item-trailing-icon-color, var(--md-sys-color-on-surface-variant, #49454f))}.list-item{background-color:var(--md-menu-item-container-color, transparent)}.list-item.selected{background-color:var(--md-menu-item-selected-container-color, var(--md-sys-color-secondary-container, #e8def8))}.selected:not(.disabled) ::slotted(*){color:var(--md-menu-item-selected-label-text-color, var(--md-sys-color-on-secondary-container, #1d192b))}@media(forced-colors: active){:host([disabled]),:host([disabled]) slot{color:GrayText;opacity:1}.list-item{position:relative}.list-item.selected::before{content:"";position:absolute;inset:0;box-sizing:border-box;border-radius:inherit;pointer-events:none;border:3px double CanvasText}}
`))},45369:function(e,t,o){o.d(t,{K:function(){return x}});o(35748),o(12977),o(95013);var r=o(69868),i=(o(36265),o(3275),o(61640),o(84922)),n=o(11991),a=o(75907),s=o(37523),l=o(78892),d=o(48521);let c,m,h,p,u,y,g,v,f=e=>e;const b=(0,l.n)(i.WF);class x extends b{get typeaheadText(){return this.menuItemController.typeaheadText}set typeaheadText(e){this.menuItemController.setTypeaheadText(e)}render(){return this.renderListItem((0,i.qy)(c||(c=f`
      <md-item>
        <div slot="container">
          ${0} ${0}
        </div>
        <slot name="start" slot="start"></slot>
        <slot name="end" slot="end"></slot>
        ${0}
      </md-item>
    `),this.renderRipple(),this.renderFocusRing(),this.renderBody()))}renderListItem(e){const t="link"===this.type;let o;switch(this.menuItemController.tagName){case"a":o=(0,s.eu)(m||(m=f`a`));break;case"button":o=(0,s.eu)(h||(h=f`button`));break;default:o=(0,s.eu)(p||(p=f`li`))}const r=t&&this.target?this.target:i.s6;return(0,s.qy)(u||(u=f`
      <${0}
        id="item"
        tabindex=${0}
        role=${0}
        aria-label=${0}
        aria-selected=${0}
        aria-checked=${0}
        aria-expanded=${0}
        aria-haspopup=${0}
        class="list-item ${0}"
        href=${0}
        target=${0}
        @click=${0}
        @keydown=${0}
      >${0}</${0}>
    `),o,this.disabled&&!t?-1:0,this.menuItemController.role,this.ariaLabel||i.s6,this.ariaSelected||i.s6,this.ariaChecked||i.s6,this.ariaExpanded||i.s6,this.ariaHasPopup||i.s6,(0,a.H)(this.getRenderClasses()),this.href||i.s6,r,this.menuItemController.onClick,this.menuItemController.onKeydown,e,o)}renderRipple(){return(0,i.qy)(y||(y=f` <md-ripple
      part="ripple"
      for="item"
      ?disabled=${0}></md-ripple>`),this.disabled)}renderFocusRing(){return(0,i.qy)(g||(g=f` <md-focus-ring
      part="focus-ring"
      for="item"
      inward></md-focus-ring>`))}getRenderClasses(){return{disabled:this.disabled,selected:this.selected}}renderBody(){return(0,i.qy)(v||(v=f`
      <slot></slot>
      <slot name="overline" slot="overline"></slot>
      <slot name="headline" slot="headline"></slot>
      <slot name="supporting-text" slot="supporting-text"></slot>
      <slot
        name="trailing-supporting-text"
        slot="trailing-supporting-text"></slot>
    `))}focus(){var e;null===(e=this.listItemRoot)||void 0===e||e.focus()}constructor(){super(...arguments),this.disabled=!1,this.type="menuitem",this.href="",this.target="",this.keepOpen=!1,this.selected=!1,this.menuItemController=new d.X(this,{getHeadlineElements:()=>this.headlineElements,getSupportingTextElements:()=>this.supportingTextElements,getDefaultElements:()=>this.defaultElements,getInteractiveElement:()=>this.listItemRoot})}}x.shadowRootOptions=Object.assign(Object.assign({},i.WF.shadowRootOptions),{},{delegatesFocus:!0}),(0,r.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],x.prototype,"disabled",void 0),(0,r.__decorate)([(0,n.MZ)()],x.prototype,"type",void 0),(0,r.__decorate)([(0,n.MZ)()],x.prototype,"href",void 0),(0,r.__decorate)([(0,n.MZ)()],x.prototype,"target",void 0),(0,r.__decorate)([(0,n.MZ)({type:Boolean,attribute:"keep-open"})],x.prototype,"keepOpen",void 0),(0,r.__decorate)([(0,n.MZ)({type:Boolean})],x.prototype,"selected",void 0),(0,r.__decorate)([(0,n.P)(".list-item")],x.prototype,"listItemRoot",void 0),(0,r.__decorate)([(0,n.KN)({slot:"headline"})],x.prototype,"headlineElements",void 0),(0,r.__decorate)([(0,n.KN)({slot:"supporting-text"})],x.prototype,"supportingTextElements",void 0),(0,r.__decorate)([(0,n.gZ)({slot:""})],x.prototype,"defaultElements",void 0),(0,r.__decorate)([(0,n.MZ)({attribute:"typeahead-text"})],x.prototype,"typeaheadText",null)}}]);
//# sourceMappingURL=7730.e452a955ed62b15b.js.map