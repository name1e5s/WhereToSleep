import React from "react";
import {
  Alert,
  ButtonToolbar,
  ButtonGroup,
  Card,
  CardBody,
  CardTitle,
  Button,
  Form,
  FormSelect,
  FormGroup,
  Container,
  Row,
  Col,
  FormCheckbox,
} from "shards-react";
import axios from "axios";

const specialDate = [
  "2020-10-04",
  "2020-10-10",
  "2020-10-17",
  "2020-10-24",
  "2020-11-07",
].map((date) => new Date(date).toDateString());

function checkSpecialDate() {
  const today = new Date();
  return specialDate.indexOf(today.toDateString());
}

function getDateDiff() {
  const date = new Date();
  const startDate = new Date("2021-03-01");
  startDate.setTime(startDate.getTime() + date.getTimezoneOffset() * 60 * 1000);
  return Math.floor((date - startDate) / (24 * 3600 * 1000));
}

function getTime() {
  const array = [
    845,
    935,
    1035,
    1125,
    1215,
    1345,
    1435,
    1530,
    1625,
    1720,
    1810,
    1915,
    2005,
    2055,
  ];
  const now = new Date();
  const hour = now.getHours();
  const minutes = now.getMinutes();
  const timeOfDay = hour * 100 + minutes;
  for (var i = 0; i < array.length; i++) {
    if (timeOfDay < array[i]) {
      return i + 1;
    }
  }
  return 1;
}

function getEndTime(startTime) {
  if (startTime < 5) {
    return 5;
  }
  if (startTime < 9) {
    return 9;
  }
  if (startTime < 11) {
    return 11;
  }
  return 14;
}

function getDefaultSelectedArray() {
  const startTime = getTime();
  const endTime = getEndTime(startTime);
  var selectedArray = Array(15).fill(false);
  for (var i = 1; i < 15; i += 1) {
    if (i >= startTime && i <= endTime) {
      selectedArray[i] = true;
    }
  }
  return selectedArray;
}

function getWeek(dateDiff) {
  const index = checkSpecialDate();
  if (index !== -1) {
    if (index < 5) {
      return 17;
    }
    return 18;
  }
  return Math.floor(dateDiff / 7) + 1;
}

function getDay(dateDiff) {
  const index = checkSpecialDate();
  if (index !== -1) {
    return (index % 5) + 1;
  }
  return Math.floor(dateDiff % 7) + 1;
}

function getRealWeek(dateDiff) {
  return Math.floor(dateDiff / 7) + 1;
}

function getRealDay(dateDiff) {
  return Math.floor(dateDiff % 7) + 1;
}

class MainContent extends React.Component {
  constructor(props) {
    super(props);
    const dateDiff = getDateDiff();
    this.state = {
      jwgl_has_data: true,
      jwgl: checkSpecialDate() === -1 ? true : false,
      selected: getDefaultSelectedArray(),
      week: "" + getWeek(dateDiff),
      day: "" + getDay(dateDiff),
      realWeek: "" + getRealWeek(dateDiff),
      realDay: "" + getRealDay(dateDiff),
      time: "" + getTime(),
      result: [],
    };

    const jwgl_status_url = "https://name1e5s.fun:4514/jwgl_has_data";
    axios.get(jwgl_status_url).then((res) => {
      this.setState({ jwgl_has_data: res.data.result });
      this.setState({ jwgl: res.data.result });
    });

    this.setWeek = this.setWeek.bind(this);
    this.setDay = this.setDay.bind(this);
    this.setTime = this.setTime.bind(this);
    this.setSelect = this.setSelect.bind(this);
    this.rangeChecked = this.rangeChecked.bind(this);
    this.getNewResult = this.getNewResult.bind(this);
    this.renderButton = this.renderButton.bind(this);
    this.renderButtons = this.renderButtons.bind(this);
    this.renderButtonToolbar = this.renderButtonToolbar.bind(this);
    this.renderSingleUnit = this.renderSingleUnit.bind(this);
    this.renderSingleClassRoom = this.renderSingleClassRoom.bind(this);
    this.renderResult = this.renderResult.bind(this);
  }

  setWeek(value) {
    this.setState({ week: value });
  }

  setDay(value) {
    this.setState({ day: value });
  }

  setTime(value) {
    this.setState({ time: value });
  }

  setSelect(i) {
    var sel = this.state.selected.slice();
    sel[i] = !this.state.selected[i];
    this.setState({ selected: sel });
  }

  rangeChecked() {
    if (this.state.jwgl_has_data) {
      this.setState({ jwgl: !this.state.jwgl });
    }
    const dateDiff = getDateDiff();
    this.setWeek("" + getWeek(dateDiff),);
    this.setDay("" + getDay(dateDiff),);
  }

  getTimeString() {
    var time_string = "";
    for (var i = 0; i < 15; i++) {
      if (this.state.selected[i]) {
        time_string += "&time=" + i;
      }
    }
    return time_string;
  }

  getNewResult() {
    if (!this.state.selected.reduce((a, b) => a || b)) {
      alert("请至少点选一个时间段");
    } else {
      const prefix = this.state.jwgl
        ? "https://name1e5s.fun:4514/free_classrooms_jwgl?week="
        : "https://name1e5s.fun:4514/free_classrooms?week=";
      const week = this.state.jwgl ? this.state.realWeek : this.state.week;
      const day = this.state.jwgl ? this.state.realDay : this.state.day;
      const url = prefix + week + "&day=" + day + this.getTimeString();
      axios
        .get(url)
        .then((res) => {
          this.setState({ result: res.data });
          if (res.data.length === 0) {
            alert(
              "暂无空教室，试试课表/考表数据吧\nPS：教务系统的空教室信息每晚零点自动更新"
            );
          }
        })
        .catch((error) => {
          alert("网络故障\nPS：最近校园网不稳定，可以切换到流量后再试试");
        });
    }
  }

  renderButton(i) {
    if (i === 15) {
      return (
        <Button theme="light" disabled className="w-100">
          {i}
        </Button>
      );
    }
    return (
      <Button
        type="button"
        className="w-100"
        theme={this.state.selected[i] ? "primary" : "light"}
        onClick={(e) => {
          this.setSelect(i);
        }}
      >
        {i < 10 ? "" + i : i}
        <a href="#"></a>
      </Button>
    );
  }

  renderButtons(start) {
    const buttons = [];
    for (var i = start; i < start + 5; i++) {
      buttons.push(this.renderButton(i));
    }
    return buttons;
  }

  renderButtonToolbar() {
    return (
      <Container>
        <ButtonToolbar className="w-100">
          <ButtonGroup size="sm" className="d-flex w-100">
            {this.renderButtons(1)}
          </ButtonGroup>
        </ButtonToolbar>
        <ButtonToolbar className="w-100">
          <ButtonGroup size="sm" className="d-flex w-100">
            {this.renderButtons(6)}
          </ButtonGroup>
        </ButtonToolbar>
        <ButtonToolbar className="w-100">
          <ButtonGroup size="sm" className="d-flex w-100">
            {this.renderButtons(11)}
          </ButtonGroup>
        </ButtonToolbar>
      </Container>
    );
  }

  renderSingleClassRoom(classroom) {
    return (
      <tr className="table-default text-center" key={classroom.name}>
        <td>{classroom.name}</td>
        <td>{classroom.seats}</td>
      </tr>
    );
  }

  renderSingleUnit(unit) {
    return (
      <Row className="mt-2">
        <Col sm="12" lg={{ size: 8, order: 2, offset: 2 }}>
          <Card>
            <CardBody>
              <CardTitle>{unit.building}</CardTitle>
              <Container>
                <Row>
                  <Col sm="12" lg={{ size: 8, order: 2, offset: 2 }}>
                    <table className="table table-hover" sm="12">
                      <thead>
                        <tr>
                          <th scope="col" className="border-0 text-center">
                            教室
                          </th>
                          <th scope="col" className="border-0 text-center">
                            座椅数
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {unit.classrooms.map(this.renderSingleClassRoom)}
                      </tbody>
                    </table>
                  </Col>
                </Row>
              </Container>
            </CardBody>
          </Card>
        </Col>
      </Row>
    );
  }

  renderResult() {
    if (!this.state.result) {
      return <></>;
    }
    return this.state.result.map(this.renderSingleUnit);
  }

  renderTime() {
    if (true) {
      return (
        <FormGroup>
          <label htmlFor="time">节次</label>
          {this.renderButtonToolbar()}
        </FormGroup>
      );
    }
    return (
      <FormGroup>
        <label htmlFor="time">节次</label>
        <FormSelect
          id="time"
          value={this.state.time}
          onChange={(e) => this.setTime(e.target.value)}
        >
          <option value="1">第 1 节</option>
          <option value="2">第 2 节</option>
          <option value="3">第 3 节</option>
          <option value="4">第 4 节</option>
          <option value="5">第 5 节</option>
          <option value="6">第 6 节</option>
          <option value="7">第 7 节</option>
          <option value="8">第 8 节</option>
          <option value="9">第 9 节</option>
          <option value="10">第 10 节</option>
          <option value="11">第 11 节</option>
          <option value="12">第 12 节</option>
          <option value="13">第 13 节</option>
          <option value="14">第 14 节</option>
        </FormSelect>
      </FormGroup>
    );
  }

  renderAlert() {
    if (!this.state.jwgl_has_data) {
      return (
        <Col sm="12" lg={{ size: 8, order: 2, offset: 2 }}>
          <Alert theme="warning">
            <b>教务系统崩了 - 请使用课表数据</b>
          </Alert>
        </Col>
      );
    }
    return <></>;
  }

  render() {
    return (
      <Container className="mt-3 mb-4">
        <Row>
          {this.renderAlert()}
          <Col sm="12" lg={{ size: 8, order: 2, offset: 2 }}>
            <Card>
              <CardBody>
                <Form>
                  <FormGroup>
                    <label htmlFor="mode">数据来源</label>
                    <FormCheckbox
                      toggle
                      checked={this.state.jwgl}
                      disabled={!this.state.jwgl_has_data}
                      onChange={this.rangeChecked}
                    >
                      {this.state.jwgl ? "教务系统" : "课表/考表"}
                    </FormCheckbox>
                  </FormGroup>
                  <FormGroup>
                    <label htmlFor="week">周次</label>
                    <FormSelect
                      id="week"
                      value={this.state.week}
                      disabled={this.state.jwgl}
                      onChange={(e) => {
                        if(!this.state.jwgl) {
                          this.setWeek(e.target.value)
                        }
                      }}
                    >
                      <option value="1">第 1 周</option>
                      <option value="2">第 2 周</option>
                      <option value="3">第 3 周</option>
                      <option value="4">第 4 周</option>
                      <option value="5">第 5 周</option>
                      <option value="6">第 6 周</option>
                      <option value="7">第 7 周</option>
                      <option value="8">第 8 周</option>
                      <option value="9">第 9 周</option>
                      <option value="10">第 10 周</option>
                      <option value="11">第 11 周</option>
                      <option value="12">第 12 周</option>
                      <option value="13">第 13 周</option>
                      <option value="14">第 14 周</option>
                      <option value="15">第 15 周</option>
                      <option value="16">第 16 周</option>
                      <option value="17">第 17 周</option>
                      <option value="18">第 18 周</option>
                    </FormSelect>
                  </FormGroup>
                  <FormGroup>
                    <label htmlFor="day">日期</label>
                    <FormSelect
                      id="day"
                      value={this.state.day}
                      disabled={this.state.jwgl}
                      onChange={(e) => {
                        if(!this.state.jwgl) {
                          this.setDay(e.target.value)
                        }
                      }}
                    >
                      <option value="1">周一</option>
                      <option value="2">周二</option>
                      <option value="3">周三</option>
                      <option value="4">周四</option>
                      <option value="5">周五</option>
                      <option value="6">周六</option>
                      <option value="7">周日</option>
                    </FormSelect>
                  </FormGroup>
                  {this.renderTime()}
                  <center>
                    <Button pill type="button" onClick={this.getNewResult}>
                      查看空闲教室
                    </Button>
                  </center>
                </Form>
              </CardBody>
            </Card>
          </Col>
        </Row>
        {this.renderResult()}
      </Container>
    );
  }
}

export default MainContent;
