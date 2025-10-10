"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["9092"],{895:function(e,t,a){a.a(e,(async function(e,i){try{a.d(t,{PE:function(){return c}});a(79827);var o=a(96904),s=a(6423),r=a(95075),n=e([o]);o=(n.then?(await n)():n)[0];const l=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"],c=e=>e.first_weekday===r.zt.language?"weekInfo"in Intl.Locale.prototype?new Intl.Locale(e.language).weekInfo.firstDay%7:(0,s.S)(e.language)%7:l.includes(e.first_weekday)?l.indexOf(e.first_weekday):1;i()}catch(l){i(l)}}))},48505:function(e,t,a){a.a(e,(async function(e,i){try{a.d(t,{LW:function(){return v},Xs:function(){return p},fU:function(){return c},ie:function(){return h}});var o=a(96904),s=a(65940),r=a(61608),n=a(56044),l=e([o,r]);[o,r]=l.then?(await l)():l;const c=(e,t,a)=>d(t,a.time_zone).format(e),d=(0,s.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{hour:"numeric",minute:"2-digit",hourCycle:(0,n.J)(e)?"h12":"h23",timeZone:(0,r.w)(e.time_zone,t)}))),h=(e,t,a)=>u(t,a.time_zone).format(e),u=(0,s.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{hour:(0,n.J)(e)?"numeric":"2-digit",minute:"2-digit",second:"2-digit",hourCycle:(0,n.J)(e)?"h12":"h23",timeZone:(0,r.w)(e.time_zone,t)}))),p=(e,t,a)=>_(t,a.time_zone).format(e),_=(0,s.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{weekday:"long",hour:(0,n.J)(e)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,n.J)(e)?"h12":"h23",timeZone:(0,r.w)(e.time_zone,t)}))),v=(e,t,a)=>m(t,a.time_zone).format(e),m=(0,s.A)(((e,t)=>new Intl.DateTimeFormat("en-GB",{hour:"numeric",minute:"2-digit",hour12:!1,timeZone:(0,r.w)(e.time_zone,t)})));i()}catch(c){i(c)}}))},61608:function(e,t,a){a.a(e,(async function(e,i){try{a.d(t,{w:function(){return u}});var o,s,r,n=a(96904),l=a(95075),c=e([n]);n=(c.then?(await c)():c)[0];const d=null===(o=Intl.DateTimeFormat)||void 0===o||null===(s=(r=o.call(Intl)).resolvedOptions)||void 0===s?void 0:s.call(r).timeZone,h=null!=d?d:"UTC",u=(e,t)=>e===l.Wj.local&&d?h:t;i()}catch(d){i(d)}}))},56044:function(e,t,a){a.d(t,{J:function(){return s}});a(79827),a(18223);var i=a(65940),o=a(95075);const s=(0,i.A)((e=>{if(e.time_format===o.Hg.language||e.time_format===o.Hg.system){const t=e.time_format===o.Hg.language?e.language:void 0;return new Date("January 1, 2023 22:00:00").toLocaleString(t).includes("10")}return e.time_format===o.Hg.am_pm}))},15785:function(e,t,a){a.a(e,(async function(e,i){try{a.r(t),a.d(t,{HaIconPicker:function(){return $}});a(79827),a(35748),a(99342),a(35058),a(65315),a(837),a(22416),a(37089),a(59023),a(5934),a(88238),a(34536),a(16257),a(20152),a(44711),a(72108),a(77030),a(18223),a(95013);var o=a(69868),s=a(84922),r=a(11991),n=a(65940),l=a(73120),c=a(73314),d=a(5177),h=(a(81164),a(36137),e([d]));d=(h.then?(await h)():h)[0];let u,p,_,v,m,g=e=>e,y=[],f=!1;const b=async()=>{f=!0;const e=await a.e("4765").then(a.t.bind(a,43692,19));y=e.default.map((e=>({icon:`mdi:${e.name}`,parts:new Set(e.name.split("-")),keywords:e.keywords})));const t=[];Object.keys(c.y).forEach((e=>{t.push(w(e))})),(await Promise.all(t)).forEach((e=>{y.push(...e)}))},w=async e=>{try{const t=c.y[e].getIconList;if("function"!=typeof t)return[];const a=await t();return a.map((t=>{var a;return{icon:`${e}:${t.name}`,parts:new Set(t.name.split("-")),keywords:null!==(a=t.keywords)&&void 0!==a?a:[]}}))}catch(t){return console.warn(`Unable to load icon list for ${e} iconset`),[]}},k=e=>(0,s.qy)(u||(u=g`
  <ha-combo-box-item type="button">
    <ha-icon .icon=${0} slot="start"></ha-icon>
    ${0}
  </ha-combo-box-item>
`),e.icon,e.icon);class $ extends s.WF{render(){return(0,s.qy)(p||(p=g`
      <ha-combo-box
        .hass=${0}
        item-value-path="icon"
        item-label-path="icon"
        .value=${0}
        allow-custom-value
        .dataProvider=${0}
        .label=${0}
        .helper=${0}
        .disabled=${0}
        .required=${0}
        .placeholder=${0}
        .errorMessage=${0}
        .invalid=${0}
        .renderer=${0}
        icon
        @opened-changed=${0}
        @value-changed=${0}
      >
        ${0}
      </ha-combo-box>
    `),this.hass,this._value,f?this._iconProvider:void 0,this.label,this.helper,this.disabled,this.required,this.placeholder,this.errorMessage,this.invalid,k,this._openedChanged,this._valueChanged,this._value||this.placeholder?(0,s.qy)(_||(_=g`
              <ha-icon .icon=${0} slot="icon">
              </ha-icon>
            `),this._value||this.placeholder):(0,s.qy)(v||(v=g`<slot slot="icon" name="fallback"></slot>`)))}async _openedChanged(e){e.detail.value&&!f&&(await b(),this.requestUpdate())}_valueChanged(e){e.stopPropagation(),this._setValue(e.detail.value)}_setValue(e){this.value=e,(0,l.r)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}get _value(){return this.value||""}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.invalid=!1,this._filterIcons=(0,n.A)(((e,t=y)=>{if(!e)return t;const a=[],i=(e,t)=>a.push({icon:e,rank:t});for(const o of t)o.parts.has(e)?i(o.icon,1):o.keywords.includes(e)?i(o.icon,2):o.icon.includes(e)?i(o.icon,3):o.keywords.some((t=>t.includes(e)))&&i(o.icon,4);return 0===a.length&&i(e,0),a.sort(((e,t)=>e.rank-t.rank))})),this._iconProvider=(e,t)=>{const a=this._filterIcons(e.filter.toLowerCase(),y),i=e.page*e.pageSize,o=i+e.pageSize;t(a.slice(i,o),a.length)}}}$.styles=(0,s.AH)(m||(m=g`
    *[slot="icon"] {
      color: var(--primary-text-color);
      position: relative;
      bottom: 2px;
    }
    *[slot="prefix"] {
      margin-right: 8px;
      margin-inline-end: 8px;
      margin-inline-start: initial;
    }
  `)),(0,o.__decorate)([(0,r.MZ)({attribute:!1})],$.prototype,"hass",void 0),(0,o.__decorate)([(0,r.MZ)()],$.prototype,"value",void 0),(0,o.__decorate)([(0,r.MZ)()],$.prototype,"label",void 0),(0,o.__decorate)([(0,r.MZ)()],$.prototype,"helper",void 0),(0,o.__decorate)([(0,r.MZ)()],$.prototype,"placeholder",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"error-message"})],$.prototype,"errorMessage",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],$.prototype,"disabled",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],$.prototype,"required",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],$.prototype,"invalid",void 0),$=(0,o.__decorate)([(0,r.EM)("ha-icon-picker")],$),i()}catch(u){i(u)}}))},97343:function(e,t,a){a.a(e,(async function(e,i){try{a.r(t);a(35748),a(99342),a(65315),a(22416),a(12977),a(62928),a(5934),a(95013);var o=a(69868),s=a(65808),r=a(7086),n=a(66633),l=a(2774),c=a(85684),d=a(21097),h=a(91927),u=a(87527),p=a(84922),_=a(11991),v=a(895),m=a(48505),g=a(56044),y=a(73120),f=a(15785),b=(a(11934),a(26004)),w=a(95075),k=a(79802),$=a(83566),x=e([f,l,n,s,v,m]);[f,l,n,s,v,m]=x.then?(await x)():x;let I,C,O=e=>e;const z={plugins:[l.A,n.Ay],headerToolbar:!1,initialView:"timeGridWeek",editable:!0,selectable:!0,selectMirror:!0,selectOverlap:!1,eventOverlap:!1,allDaySlot:!1,height:"parent",locales:r.A,firstDay:1,dayHeaderFormat:{weekday:"short",month:void 0,day:void 0}};class j extends p.WF{set item(e){this._item=e,e?(this._name=e.name||"",this._icon=e.icon||"",this._monday=e.monday||[],this._tuesday=e.tuesday||[],this._wednesday=e.wednesday||[],this._thursday=e.thursday||[],this._friday=e.friday||[],this._saturday=e.saturday||[],this._sunday=e.sunday||[]):(this._name="",this._icon="",this._monday=[],this._tuesday=[],this._wednesday=[],this._thursday=[],this._friday=[],this._saturday=[],this._sunday=[])}disconnectedCallback(){var e,t;super.disconnectedCallback(),null===(e=this.calendar)||void 0===e||e.destroy(),this.calendar=void 0,null===(t=this.renderRoot.querySelector("style[data-fullcalendar]"))||void 0===t||t.remove()}connectedCallback(){super.connectedCallback(),this.hasUpdated&&!this.calendar&&this._setupCalendar()}focus(){this.updateComplete.then((()=>{var e;return null===(e=this.shadowRoot)||void 0===e||null===(e=e.querySelector("[dialogInitialFocus]"))||void 0===e?void 0:e.focus()}))}render(){return this.hass?(0,p.qy)(I||(I=O`
      <div class="form">
        <ha-textfield
          .value=${0}
          .configValue=${0}
          @input=${0}
          .label=${0}
          autoValidate
          required
          .validationMessage=${0}
          dialogInitialFocus
        ></ha-textfield>
        <ha-icon-picker
          .hass=${0}
          .value=${0}
          .configValue=${0}
          @value-changed=${0}
          .label=${0}
        ></ha-icon-picker>
        <div id="calendar"></div>
      </div>
    `),this._name,"name",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.name"),this.hass.localize("ui.dialogs.helper_settings.required_error_msg"),this.hass,this._icon,"icon",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.icon")):p.s6}willUpdate(e){if(super.willUpdate(e),!this.calendar)return;(e.has("_sunday")||e.has("_monday")||e.has("_tuesday")||e.has("_wednesday")||e.has("_thursday")||e.has("_friday")||e.has("_saturday")||e.has("calendar"))&&(this.calendar.removeAllEventSources(),this.calendar.addEventSource(this._events));const t=e.get("hass");t&&t.language!==this.hass.language&&this.calendar.setOption("locale",this.hass.language)}firstUpdated(){this._setupCalendar()}_setupCalendar(){const e=Object.assign(Object.assign({},z),{},{locale:this.hass.language,firstDay:(0,v.PE)(this.hass.locale),slotLabelFormat:{hour:"numeric",minute:void 0,hour12:(0,g.J)(this.hass.locale),meridiem:!!(0,g.J)(this.hass.locale)&&"narrow"},eventTimeFormat:{hour:(0,g.J)(this.hass.locale)?"numeric":"2-digit",minute:(0,g.J)(this.hass.locale)?"numeric":"2-digit",hour12:(0,g.J)(this.hass.locale),meridiem:!!(0,g.J)(this.hass.locale)&&"narrow"}});e.eventClick=e=>this._handleEventClick(e),e.select=e=>this._handleSelect(e),e.eventResize=e=>this._handleEventResize(e),e.eventDrop=e=>this._handleEventDrop(e),this.calendar=new s.Vv(this.shadowRoot.getElementById("calendar"),e),this.calendar.render()}get _events(){const e=[];for(const[t,a]of b.mx.entries())this[`_${a}`].length&&this[`_${a}`].forEach(((i,o)=>{let s=(0,c.s)(new Date,t);(0,d.R)(s,new Date,{weekStartsOn:(0,v.PE)(this.hass.locale)})||(s=(0,h.f)(s,-7));const r=new Date(s),n=i.from.split(":");r.setHours(parseInt(n[0]),parseInt(n[1]),0,0);const l=new Date(s),u=i.to.split(":");l.setHours(parseInt(u[0]),parseInt(u[1]),0,0),e.push({id:`${a}-${o}`,start:r.toISOString(),end:l.toISOString()})}));return e}_handleSelect(e){const{start:t,end:a}=e,i=b.mx[t.getDay()],o=[...this[`_${i}`]],s=Object.assign({},this._item),r=(0,m.LW)(a,Object.assign(Object.assign({},this.hass.locale),{},{time_zone:w.Wj.local}),this.hass.config);o.push({from:(0,m.LW)(t,Object.assign(Object.assign({},this.hass.locale),{},{time_zone:w.Wj.local}),this.hass.config),to:(0,u.r)(t,a)&&"0:00"!==r?r:"24:00"}),s[i]=o,(0,y.r)(this,"value-changed",{value:s}),(0,u.r)(t,a)||this.calendar.unselect()}_handleEventResize(e){const{id:t,start:a,end:i}=e.event,[o,s]=t.split("-"),r=this[`_${o}`][parseInt(s)],n=Object.assign({},this._item),l=(0,m.LW)(i,this.hass.locale,this.hass.config);n[o][s]=Object.assign(Object.assign({},n[o][s]),{},{from:r.from,to:(0,u.r)(a,i)&&"0:00"!==l?l:"24:00"}),(0,y.r)(this,"value-changed",{value:n}),(0,u.r)(a,i)||(this.requestUpdate(`_${o}`),e.revert())}_handleEventDrop(e){const{id:t,start:a,end:i}=e.event,[o,s]=t.split("-"),r=b.mx[a.getDay()],n=Object.assign({},this._item),l=(0,m.LW)(i,this.hass.locale,this.hass.config),c=Object.assign(Object.assign({},n[o][s]),{},{from:(0,m.LW)(a,this.hass.locale,this.hass.config),to:(0,u.r)(a,i)&&"0:00"!==l?l:"24:00"});if(r===o)n[o][s]=c;else{n[o].splice(s,1);const e=[...this[`_${r}`]];e.push(c),n[r]=e}(0,y.r)(this,"value-changed",{value:n}),(0,u.r)(a,i)||(this.requestUpdate(`_${o}`),e.revert())}async _handleEventClick(e){const[t,a]=e.event.id.split("-"),i=[...this[`_${t}`]][a];(0,k.c)(this,{block:i,updateBlock:e=>this._updateBlock(t,a,e),deleteBlock:()=>this._deleteBlock(t,a)})}_updateBlock(e,t,a){const[i,o,s]=a.from.split(":");a.from=`${i}:${o}`;const[r,n,l]=a.to.split(":");a.to=`${r}:${n}`,0===Number(r)&&0===Number(n)&&(a.to="24:00");const c=Object.assign({},this._item);c[e]=[...this._item[e]],c[e][t]=a,(0,y.r)(this,"value-changed",{value:c})}_deleteBlock(e,t){const a=[...this[`_${e}`]],i=Object.assign({},this._item);a.splice(parseInt(t),1),i[e]=a,(0,y.r)(this,"value-changed",{value:i})}_valueChanged(e){var t;if(!this.new&&!this._item)return;e.stopPropagation();const a=e.target.configValue,i=(null===(t=e.detail)||void 0===t?void 0:t.value)||e.target.value;if(this[`_${a}`]===i)return;const o=Object.assign({},this._item);i?o[a]=i:delete o[a],(0,y.r)(this,"value-changed",{value:o})}static get styles(){return[$.RF,(0,p.AH)(C||(C=O`
        .form {
          color: var(--primary-text-color);
        }

        ha-textfield {
          display: block;
          margin: 8px 0;
        }

        #calendar {
          margin: 8px 0;
          height: 450px;
          width: 100%;
          -webkit-user-select: none;
          -ms-user-select: none;
          user-select: none;
          --fc-border-color: var(--divider-color);
          --fc-event-border-color: var(--divider-color);
        }

        .fc-v-event .fc-event-time {
          white-space: inherit;
        }
        .fc-theme-standard .fc-scrollgrid {
          border: 1px solid var(--divider-color);
          border-radius: var(--mdc-shape-small, 4px);
        }

        .fc-scrollgrid-section-header td {
          border: none;
        }
        :host([narrow]) .fc-scrollgrid-sync-table {
          overflow: hidden;
        }
        table.fc-scrollgrid-sync-table
          tbody
          tr:first-child
          .fc-daygrid-day-top {
          padding-top: 0;
        }
        .fc-scroller::-webkit-scrollbar {
          width: 0.4rem;
          height: 0.4rem;
        }
        .fc-scroller::-webkit-scrollbar-thumb {
          -webkit-border-radius: 4px;
          border-radius: 4px;
          background: var(--scrollbar-thumb-color);
        }
        .fc-scroller {
          overflow-y: auto;
          scrollbar-color: var(--scrollbar-thumb-color) transparent;
          scrollbar-width: thin;
        }

        .fc-timegrid-event-short .fc-event-time:after {
          content: ""; /* prevent trailing dash in half hour events since we do not have event titles */
        }

        a {
          color: inherit !important;
        }

        th.fc-col-header-cell.fc-day {
          background-color: var(--table-header-background-color);
          color: var(--primary-text-color);
          font-size: var(--ha-font-size-xs);
          font-weight: var(--ha-font-weight-bold);
          text-transform: uppercase;
        }
      `))]}constructor(...e){super(...e),this.new=!1}}(0,o.__decorate)([(0,_.MZ)({attribute:!1})],j.prototype,"hass",void 0),(0,o.__decorate)([(0,_.MZ)({type:Boolean})],j.prototype,"new",void 0),(0,o.__decorate)([(0,_.wk)()],j.prototype,"_name",void 0),(0,o.__decorate)([(0,_.wk)()],j.prototype,"_icon",void 0),(0,o.__decorate)([(0,_.wk)()],j.prototype,"_monday",void 0),(0,o.__decorate)([(0,_.wk)()],j.prototype,"_tuesday",void 0),(0,o.__decorate)([(0,_.wk)()],j.prototype,"_wednesday",void 0),(0,o.__decorate)([(0,_.wk)()],j.prototype,"_thursday",void 0),(0,o.__decorate)([(0,_.wk)()],j.prototype,"_friday",void 0),(0,o.__decorate)([(0,_.wk)()],j.prototype,"_saturday",void 0),(0,o.__decorate)([(0,_.wk)()],j.prototype,"_sunday",void 0),(0,o.__decorate)([(0,_.wk)()],j.prototype,"calendar",void 0),j=(0,o.__decorate)([(0,_.EM)("ha-schedule-form")],j),i()}catch(I){i(I)}}))},79802:function(e,t,a){a.d(t,{c:function(){return s}});a(35748),a(5934),a(95013);var i=a(73120);const o=()=>a.e("6107").then(a.bind(a,90806)),s=(e,t)=>{(0,i.r)(e,"show-dialog",{dialogTag:"dialog-schedule-block-info",dialogImport:o,dialogParams:t})}}}]);
//# sourceMappingURL=9092.172b2216f00d10e7.js.map