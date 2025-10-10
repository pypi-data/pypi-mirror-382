import React, {
  type ChangeEvent,
  type MouseEvent,
  useEffect,
  useState
} from 'react';
import {
  Button,
  Container,
  InputLabel,
  MenuItem,
  Popover,
  Select,
  type SelectChangeEvent,
  Stack,
  TextField,
  Typography
} from '@mui/material';
import { grey } from '@mui/material/colors';
import EventRepeatIcon from '@mui/icons-material/EventRepeat';
import dayjs, { type Dayjs } from 'dayjs';
import advancedFormat from 'dayjs/plugin/advancedFormat';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';

dayjs.extend(advancedFormat);

type PeriodUnit = 'hour' | 'day' | 'week' | 'month';

const defaultPeriodUnit = 'day';

function getDefaultStartTime() {
  // Pick a random time in the middle of the night
  const hour = getRandomItem([22, 23, 0, 1, 2, 3, 4, 5]);
  const minute = getRandomInt(0, 59);
  return dayjs().hour(hour).minute(minute);
}

function getRandomInt(min: number, max: number) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function getRandomItem<T>(choices: Array<T>): T {
  return choices[getRandomInt(0, choices.length - 1)];
}

function getCron(periodUnit: PeriodUnit, startTime: Dayjs): string {
  switch (periodUnit) {
    case 'hour':
      return `${startTime.minute()} * * * *`;
    case 'day':
      return `${startTime.minute()} ${startTime.hour()} * * *`;
    case 'week':
      return `${startTime.minute()} ${startTime.hour()} * * ${startTime.day()}`;
    case 'month':
      return `${startTime.minute()} ${startTime.hour()} ${startTime.date()} * *`;
  }
}

function getTextDescriptionShort(
  periodUnit: PeriodUnit,
  startTime: Dayjs
): string {
  switch (periodUnit) {
    case 'hour':
      return `Every hour at :${startTime.format('mm')}`;
    case 'day':
      return `Every day at ${startTime.format('HH:mm')}`;
    case 'week':
      return `Every ${startTime.format('dddd')}`;
    case 'month':
      return `On the ${startTime.format('Do')} of each month`;
  }
}

function getTextDescriptionLong(
  periodUnit: PeriodUnit,
  startTime: Dayjs
): string {
  const prefix = 'Your workflow will run ';
  switch (periodUnit) {
    case 'hour':
      return prefix + `at minute :${startTime.format('mm')}`;
    case 'day':
    case 'week':
    case 'month':
      return prefix + `during quiet hours at ${startTime.format('HH:mm')}`;
  }
}

function PeriodPicker({
  periodUnit,
  setPeriodUnit
}: {
  periodUnit: PeriodUnit;
  setPeriodUnit: (intervalType: PeriodUnit) => void;
}) {
  return (
    <Stack
      direction="row"
      spacing={2}
      style={{
        padding: '1rem',
        alignItems: 'center'
      }}
    >
      <InputLabel
        id="input-label"
        style={{
          width: '50%'
        }}
      >
        Run every
      </InputLabel>
      <Select
        id="period-interval"
        labelId="input-label"
        aria-describedby="repetion periodUnit duration"
        value={periodUnit}
        onChange={(event: SelectChangeEvent<PeriodUnit>) => {
          setPeriodUnit(event.target.value as PeriodUnit);
        }}
        style={{
          width: '50%'
        }}
        MenuProps={{
          sx: {
            zIndex: 30000
          }
        }}
      >
        <MenuItem value={'hour' as PeriodUnit}>{'hour'}</MenuItem>
        <MenuItem value={'day' as PeriodUnit}>{'day'}</MenuItem>
        <MenuItem value={'week' as PeriodUnit}>{'week'}</MenuItem>
        <MenuItem value={'month' as PeriodUnit}>{'month'}</MenuItem>
      </Select>
    </Stack>
  );
}

function DayOfWeekPicker({
  time,
  setTime
}: {
  time: Dayjs;
  setTime: (time: Dayjs) => void;
}) {
  return (
    <Stack
      direction="row"
      spacing={2}
      style={{
        padding: '1rem',
        alignItems: 'center'
      }}
    >
      <InputLabel
        id="day-of-week-label"
        style={{
          width: '40%'
        }}
      >
        On
      </InputLabel>
      <Select
        id="day-of-week-select"
        labelId="day-of-week-label"
        value={time.day()}
        onChange={(event: SelectChangeEvent<number>) => {
          setTime(time.day(Number(event.target.value)));
        }}
        style={{
          width: '60%'
        }}
        MenuProps={{
          sx: {
            zIndex: 30000
          }
        }}
      >
        <MenuItem value={1}>Monday</MenuItem>
        <MenuItem value={2}>Tuesday</MenuItem>
        <MenuItem value={3}>Wednesday</MenuItem>
        <MenuItem value={4}>Thursday</MenuItem>
        <MenuItem value={5}>Friday</MenuItem>
        <MenuItem value={6}>Saturday</MenuItem>
        <MenuItem value={0}>Sunday</MenuItem>
      </Select>
    </Stack>
  );
}

function DayOfMonthPicker({
  time,
  setTime
}: {
  time: Dayjs;
  setTime: (time: Dayjs) => void;
}) {
  return (
    <Stack
      direction="row"
      spacing={2}
      style={{
        padding: '1rem',
        alignItems: 'center'
      }}
    >
      <InputLabel
        style={{
          width: '40%'
        }}
      >
        On day
      </InputLabel>
      <TextField
        type="number"
        id="time"
        label="Day"
        value={time.date()}
        onChange={(event: ChangeEvent<HTMLInputElement>) => {
          const newDay = Number(event.target.value);
          setTime(time.date(newDay));
        }}
        style={{
          width: '60%'
        }}
      />
    </Stack>
  );
}

function TimePicker({
  periodUnit,
  time,
  setTime
}: {
  periodUnit: PeriodUnit;
  time: Dayjs;
  setTime: (time: Dayjs) => void;
}) {
  return (
    <>
      {periodUnit === 'week' && (
        <DayOfWeekPicker time={time} setTime={setTime} />
      )}
      {periodUnit === 'month' && (
        <DayOfMonthPicker time={time} setTime={setTime} />
      )}
      <Container>
        <Typography variant="body2">
          {getTextDescriptionLong(periodUnit, time)}
        </Typography>
      </Container>
    </>
  );
}

export default function WorkflowRepeatPicker({
  setCron
}: {
  setCron: (cron: string | null) => void;
}) {
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);

  const [touched, setTouched] = useState<boolean>(false);
  const [periodUnit, setPeriodUnit] = useState<PeriodUnit>(defaultPeriodUnit);
  const [startTime, setStartTime] = useState<Dayjs>(getDefaultStartTime);

  useEffect(() => {
    if (!touched) {
      setCron(null);
    } else {
      setCron(getCron(periodUnit, startTime));
    }
  }, [touched, setCron, periodUnit, startTime]);

  const handleClick = (event: MouseEvent<HTMLButtonElement>) => {
    if (!touched) {
      setPeriodUnit(defaultPeriodUnit);
    }
    setTouched(true);
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);
  const id = open ? 'simple-popover' : undefined;

  return (
    <>
      <Button
        onClick={handleClick}
        size="small"
        variant="text"
        startIcon={<EventRepeatIcon fontSize="inherit" />}
        style={{
          color: grey[900],
          textTransform: 'none',
          minWidth: '10rem'
        }}
      >
        {touched
          ? getTextDescriptionShort(periodUnit, startTime)
          : 'Make recurring'}
      </Button>
      <Popover
        id={id}
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left'
        }}
        style={{
          zIndex: 20000
        }}
      >
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <Container
            style={{
              padding: '1rem',
              minWidth: '25rem'
            }}
          >
            <PeriodPicker
              periodUnit={periodUnit}
              setPeriodUnit={setPeriodUnit}
            />
            <TimePicker
              periodUnit={periodUnit}
              time={startTime}
              setTime={setStartTime}
            />
            <Stack
              direction="row"
              spacing={2}
              style={{
                float: 'right',
                margin: '1rem'
              }}
            >
              <Button
                onClick={() => {
                  setTouched(false);
                  handleClose();
                }}
              >
                Disable
              </Button>
              <Button onClick={handleClose} variant="contained">
                Apply
              </Button>
            </Stack>
          </Container>
        </LocalizationProvider>
      </Popover>
    </>
  );
}
