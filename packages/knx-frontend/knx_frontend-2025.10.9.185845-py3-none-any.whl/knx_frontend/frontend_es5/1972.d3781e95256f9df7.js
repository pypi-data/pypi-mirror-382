"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["1972"],{36615:function(e,t,i){i(35748),i(92344),i(47849),i(95013);var a=i(69868),o=i(84922),s=i(11991),d=i(13802),l=i(73120),r=i(20674);i(93672),i(20014),i(25223),i(37207),i(11934);let n,h,u,c,p,m,b,y,v,_=e=>e;class f extends o.WF{render(){return(0,o.qy)(n||(n=_`
      ${0}
      <div class="time-input-wrap-wrap">
        <div class="time-input-wrap">
          ${0}

          <ha-textfield
            id="hour"
            type="number"
            inputmode="numeric"
            .value=${0}
            .label=${0}
            name="hours"
            @change=${0}
            @focusin=${0}
            no-spinner
            .required=${0}
            .autoValidate=${0}
            maxlength="2"
            max=${0}
            min="0"
            .disabled=${0}
            suffix=":"
            class="hasSuffix"
          >
          </ha-textfield>
          <ha-textfield
            id="min"
            type="number"
            inputmode="numeric"
            .value=${0}
            .label=${0}
            @change=${0}
            @focusin=${0}
            name="minutes"
            no-spinner
            .required=${0}
            .autoValidate=${0}
            maxlength="2"
            max="59"
            min="0"
            .disabled=${0}
            .suffix=${0}
            class=${0}
          >
          </ha-textfield>
          ${0}
          ${0}
          ${0}
        </div>

        ${0}
      </div>
      ${0}
    `),this.label?(0,o.qy)(h||(h=_`<label>${0}${0}</label>`),this.label,this.required?" *":""):o.s6,this.enableDay?(0,o.qy)(u||(u=_`
                <ha-textfield
                  id="day"
                  type="number"
                  inputmode="numeric"
                  .value=${0}
                  .label=${0}
                  name="days"
                  @change=${0}
                  @focusin=${0}
                  no-spinner
                  .required=${0}
                  .autoValidate=${0}
                  min="0"
                  .disabled=${0}
                  suffix=":"
                  class="hasSuffix"
                >
                </ha-textfield>
              `),this.days.toFixed(),this.dayLabel,this._valueChanged,this._onFocus,this.required,this.autoValidate,this.disabled):o.s6,this.hours.toFixed(),this.hourLabel,this._valueChanged,this._onFocus,this.required,this.autoValidate,(0,d.J)(this._hourMax),this.disabled,this._formatValue(this.minutes),this.minLabel,this._valueChanged,this._onFocus,this.required,this.autoValidate,this.disabled,this.enableSecond?":":"",this.enableSecond?"has-suffix":"",this.enableSecond?(0,o.qy)(c||(c=_`<ha-textfield
                id="sec"
                type="number"
                inputmode="numeric"
                .value=${0}
                .label=${0}
                @change=${0}
                @focusin=${0}
                name="seconds"
                no-spinner
                .required=${0}
                .autoValidate=${0}
                maxlength="2"
                max="59"
                min="0"
                .disabled=${0}
                .suffix=${0}
                class=${0}
              >
              </ha-textfield>`),this._formatValue(this.seconds),this.secLabel,this._valueChanged,this._onFocus,this.required,this.autoValidate,this.disabled,this.enableMillisecond?":":"",this.enableMillisecond?"has-suffix":""):o.s6,this.enableMillisecond?(0,o.qy)(p||(p=_`<ha-textfield
                id="millisec"
                type="number"
                .value=${0}
                .label=${0}
                @change=${0}
                @focusin=${0}
                name="milliseconds"
                no-spinner
                .required=${0}
                .autoValidate=${0}
                maxlength="3"
                max="999"
                min="0"
                .disabled=${0}
              >
              </ha-textfield>`),this._formatValue(this.milliseconds,3),this.millisecLabel,this._valueChanged,this._onFocus,this.required,this.autoValidate,this.disabled):o.s6,!this.clearable||this.required||this.disabled?o.s6:(0,o.qy)(m||(m=_`<ha-icon-button
                label="clear"
                @click=${0}
                .path=${0}
              ></ha-icon-button>`),this._clearValue,"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"),24===this.format?o.s6:(0,o.qy)(b||(b=_`<ha-select
              .required=${0}
              .value=${0}
              .disabled=${0}
              name="amPm"
              naturalMenuWidth
              fixedMenuPosition
              @selected=${0}
              @closed=${0}
            >
              <ha-list-item value="AM">AM</ha-list-item>
              <ha-list-item value="PM">PM</ha-list-item>
            </ha-select>`),this.required,this.amPm,this.disabled,this._valueChanged,r.d),this.helper?(0,o.qy)(y||(y=_`<ha-input-helper-text .disabled=${0}
            >${0}</ha-input-helper-text
          >`),this.disabled,this.helper):o.s6)}_clearValue(){(0,l.r)(this,"value-changed")}_valueChanged(e){const t=e.currentTarget;this[t.name]="amPm"===t.name?t.value:Number(t.value);const i={hours:this.hours,minutes:this.minutes,seconds:this.seconds,milliseconds:this.milliseconds};this.enableDay&&(i.days=this.days),12===this.format&&(i.amPm=this.amPm),(0,l.r)(this,"value-changed",{value:i})}_onFocus(e){e.currentTarget.select()}_formatValue(e,t=2){return e.toString().padStart(t,"0")}get _hourMax(){if(!this.noHoursLimit)return 12===this.format?12:23}constructor(...e){super(...e),this.autoValidate=!1,this.required=!1,this.format=12,this.disabled=!1,this.days=0,this.hours=0,this.minutes=0,this.seconds=0,this.milliseconds=0,this.dayLabel="",this.hourLabel="",this.minLabel="",this.secLabel="",this.millisecLabel="",this.enableSecond=!1,this.enableMillisecond=!1,this.enableDay=!1,this.noHoursLimit=!1,this.amPm="AM"}}f.styles=(0,o.AH)(v||(v=_`
    :host([clearable]) {
      position: relative;
    }
    .time-input-wrap-wrap {
      display: flex;
    }
    .time-input-wrap {
      display: flex;
      flex: var(--time-input-flex, unset);
      border-radius: var(--mdc-shape-small, 4px) var(--mdc-shape-small, 4px) 0 0;
      overflow: hidden;
      position: relative;
      direction: ltr;
      padding-right: 3px;
    }
    ha-textfield {
      width: 60px;
      flex-grow: 1;
      text-align: center;
      --mdc-shape-small: 0;
      --text-field-appearance: none;
      --text-field-padding: 0 4px;
      --text-field-suffix-padding-left: 2px;
      --text-field-suffix-padding-right: 0;
      --text-field-text-align: center;
    }
    ha-textfield.hasSuffix {
      --text-field-padding: 0 0 0 4px;
    }
    ha-textfield:first-child {
      --text-field-border-top-left-radius: var(--mdc-shape-medium);
    }
    ha-textfield:last-child {
      --text-field-border-top-right-radius: var(--mdc-shape-medium);
    }
    ha-select {
      --mdc-shape-small: 0;
      width: 85px;
    }
    :host([clearable]) .mdc-select__anchor {
      padding-inline-end: var(--select-selected-text-padding-end, 12px);
    }
    ha-icon-button {
      position: relative;
      --mdc-icon-button-size: 36px;
      --mdc-icon-size: 20px;
      color: var(--secondary-text-color);
      direction: var(--direction);
      display: flex;
      align-items: center;
      background-color: var(--mdc-text-field-fill-color, whitesmoke);
      border-bottom-style: solid;
      border-bottom-width: 1px;
    }
    label {
      -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
      -webkit-font-smoothing: var(--ha-font-smoothing);
      font-family: var(
        --mdc-typography-body2-font-family,
        var(--mdc-typography-font-family, var(--ha-font-family-body))
      );
      font-size: var(--mdc-typography-body2-font-size, var(--ha-font-size-s));
      line-height: var(
        --mdc-typography-body2-line-height,
        var(--ha-line-height-condensed)
      );
      font-weight: var(
        --mdc-typography-body2-font-weight,
        var(--ha-font-weight-normal)
      );
      letter-spacing: var(
        --mdc-typography-body2-letter-spacing,
        0.0178571429em
      );
      text-decoration: var(--mdc-typography-body2-text-decoration, inherit);
      text-transform: var(--mdc-typography-body2-text-transform, inherit);
      color: var(--mdc-theme-text-primary-on-background, rgba(0, 0, 0, 0.87));
      padding-left: 4px;
      padding-inline-start: 4px;
      padding-inline-end: initial;
    }
    ha-input-helper-text {
      padding-top: 8px;
      line-height: var(--ha-line-height-condensed);
    }
  `)),(0,a.__decorate)([(0,s.MZ)()],f.prototype,"label",void 0),(0,a.__decorate)([(0,s.MZ)()],f.prototype,"helper",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:"auto-validate",type:Boolean})],f.prototype,"autoValidate",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],f.prototype,"required",void 0),(0,a.__decorate)([(0,s.MZ)({type:Number})],f.prototype,"format",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],f.prototype,"disabled",void 0),(0,a.__decorate)([(0,s.MZ)({type:Number})],f.prototype,"days",void 0),(0,a.__decorate)([(0,s.MZ)({type:Number})],f.prototype,"hours",void 0),(0,a.__decorate)([(0,s.MZ)({type:Number})],f.prototype,"minutes",void 0),(0,a.__decorate)([(0,s.MZ)({type:Number})],f.prototype,"seconds",void 0),(0,a.__decorate)([(0,s.MZ)({type:Number})],f.prototype,"milliseconds",void 0),(0,a.__decorate)([(0,s.MZ)({type:String,attribute:"day-label"})],f.prototype,"dayLabel",void 0),(0,a.__decorate)([(0,s.MZ)({type:String,attribute:"hour-label"})],f.prototype,"hourLabel",void 0),(0,a.__decorate)([(0,s.MZ)({type:String,attribute:"min-label"})],f.prototype,"minLabel",void 0),(0,a.__decorate)([(0,s.MZ)({type:String,attribute:"sec-label"})],f.prototype,"secLabel",void 0),(0,a.__decorate)([(0,s.MZ)({type:String,attribute:"ms-label"})],f.prototype,"millisecLabel",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:"enable-second",type:Boolean})],f.prototype,"enableSecond",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:"enable-millisecond",type:Boolean})],f.prototype,"enableMillisecond",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:"enable-day",type:Boolean})],f.prototype,"enableDay",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:"no-hours-limit",type:Boolean})],f.prototype,"noHoursLimit",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],f.prototype,"amPm",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0})],f.prototype,"clearable",void 0),f=(0,a.__decorate)([(0,s.EM)("ha-base-time-input")],f)},76450:function(e,t,i){i(35748),i(12977),i(95013);var a=i(69868),o=i(84922),s=i(11991),d=i(73120);i(36615);let l,r=e=>e;class n extends o.WF{render(){return(0,o.qy)(l||(l=r`
      <ha-base-time-input
        .label=${0}
        .helper=${0}
        .required=${0}
        .clearable=${0}
        .autoValidate=${0}
        .disabled=${0}
        errorMessage="Required"
        enable-second
        .enableMillisecond=${0}
        .enableDay=${0}
        format="24"
        .days=${0}
        .hours=${0}
        .minutes=${0}
        .seconds=${0}
        .milliseconds=${0}
        @value-changed=${0}
        no-hours-limit
        day-label="dd"
        hour-label="hh"
        min-label="mm"
        sec-label="ss"
        ms-label="ms"
      ></ha-base-time-input>
    `),this.label,this.helper,this.required,!this.required&&void 0!==this.data,this.required,this.disabled,this.enableMillisecond,this.enableDay,this._days,this._hours,this._minutes,this._seconds,this._milliseconds,this._durationChanged)}get _days(){var e;return null!==(e=this.data)&&void 0!==e&&e.days?Number(this.data.days):this.required||this.data?0:NaN}get _hours(){var e;return null!==(e=this.data)&&void 0!==e&&e.hours?Number(this.data.hours):this.required||this.data?0:NaN}get _minutes(){var e;return null!==(e=this.data)&&void 0!==e&&e.minutes?Number(this.data.minutes):this.required||this.data?0:NaN}get _seconds(){var e;return null!==(e=this.data)&&void 0!==e&&e.seconds?Number(this.data.seconds):this.required||this.data?0:NaN}get _milliseconds(){var e;return null!==(e=this.data)&&void 0!==e&&e.milliseconds?Number(this.data.milliseconds):this.required||this.data?0:NaN}_durationChanged(e){e.stopPropagation();const t=e.detail.value?Object.assign({},e.detail.value):void 0;var i;t&&(t.hours||(t.hours=0),t.minutes||(t.minutes=0),t.seconds||(t.seconds=0),"days"in t&&(t.days||(t.days=0)),"milliseconds"in t&&(t.milliseconds||(t.milliseconds=0)),this.enableMillisecond||t.milliseconds?t.milliseconds>999&&(t.seconds+=Math.floor(t.milliseconds/1e3),t.milliseconds%=1e3):delete t.milliseconds,t.seconds>59&&(t.minutes+=Math.floor(t.seconds/60),t.seconds%=60),t.minutes>59&&(t.hours+=Math.floor(t.minutes/60),t.minutes%=60),this.enableDay&&t.hours>24&&(t.days=(null!==(i=t.days)&&void 0!==i?i:0)+Math.floor(t.hours/24),t.hours%=24));(0,d.r)(this,"value-changed",{value:t})}constructor(...e){super(...e),this.required=!1,this.enableMillisecond=!1,this.enableDay=!1,this.disabled=!1}}(0,a.__decorate)([(0,s.MZ)({attribute:!1})],n.prototype,"data",void 0),(0,a.__decorate)([(0,s.MZ)()],n.prototype,"label",void 0),(0,a.__decorate)([(0,s.MZ)()],n.prototype,"helper",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],n.prototype,"required",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:"enable-millisecond",type:Boolean})],n.prototype,"enableMillisecond",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:"enable-day",type:Boolean})],n.prototype,"enableDay",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],n.prototype,"disabled",void 0),n=(0,a.__decorate)([(0,s.EM)("ha-duration-input")],n)},3631:function(e,t,i){i.r(t),i.d(t,{HaTimeDuration:function(){return r}});i(35748),i(95013);var a=i(69868),o=i(84922),s=i(11991);i(76450);let d,l=e=>e;class r extends o.WF{render(){var e,t;return(0,o.qy)(d||(d=l`
      <ha-duration-input
        .label=${0}
        .helper=${0}
        .data=${0}
        .disabled=${0}
        .required=${0}
        .enableDay=${0}
        .enableMillisecond=${0}
      ></ha-duration-input>
    `),this.label,this.helper,this.value,this.disabled,this.required,null===(e=this.selector.duration)||void 0===e?void 0:e.enable_day,null===(t=this.selector.duration)||void 0===t?void 0:t.enable_millisecond)}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}(0,a.__decorate)([(0,s.MZ)({attribute:!1})],r.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],r.prototype,"selector",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],r.prototype,"value",void 0),(0,a.__decorate)([(0,s.MZ)()],r.prototype,"label",void 0),(0,a.__decorate)([(0,s.MZ)()],r.prototype,"helper",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],r.prototype,"disabled",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],r.prototype,"required",void 0),r=(0,a.__decorate)([(0,s.EM)("ha-selector-duration")],r)}}]);
//# sourceMappingURL=1972.d3781e95256f9df7.js.map