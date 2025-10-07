import { useEffect } from "react";
import useStartFlightWizardStore from "./stores/start_flight_wizard";
import useMissionControlStore from "./stores/mission_control";

const {
  importWhiteboxComponent,
  importWhiteboxStateStore,
} = Whitebox;

const PrimaryButton = importWhiteboxComponent("ui.button-primary");

const StepIntro = ({ title, description }) => {
  return (
    <div className="py-6">
      <h2 className="font-bold text-3xl">{title}</h2>
      <p className="font-light text-base text-gray-2">{description}</p>
    </div>
  );
};

const InstalledDevicesStep = () => {
  const DeviceList = importWhiteboxComponent("device-wizard.device-list");

  useEffect(() => {
    async function fetchDevices() {
      const useDevicesStore = await importWhiteboxStateStore("devices");
      const _fetchDevices = useDevicesStore.getState().fetchDevices;
      _fetchDevices();
    }

    fetchDevices();
  }, []);

  return (
    <>
      <StepIntro
        title="Installed Devices"
        description="To get the best experience, ensure that your devices are connected."
      />
      <DeviceList />
    </>
  );
};

const PreviewConnectedDevicesStep = () => {
  const InputPreview = importWhiteboxComponent("device.camera-input-preview");

  return (
    <>
      <StepIntro
        title="Preview Connected Devices"
        description="Preview the inputs to ensure everything is in place and connected."
      />
      <InputPreview />
    </>
  );
};

const LocationInput = ({ leftIcon, placeholder }) => {
  return (
    <div className="flex flex-row border border-gray-4 rounded-full px-6 py-4 mb-4 items-center">
      {leftIcon && <div className="mr-4">{leftIcon}</div>}
      <input
        type="text"
        placeholder={placeholder}
        className="flex-1 outline-none font-light"
      />
    </div>
  );
};

const WaypointInput = () => {
  const LocationOnIcon = importWhiteboxComponent("icons.location-on");
  const Trash2Icon = importWhiteboxComponent("icons.trash-2");
  const DragIndicatorIcon = importWhiteboxComponent("icons.drag-indicator");

  return (
    <div className="relative flex flex-row w-full items-center gap-4 mb-4">
      <div className="flex flex-row border border-gray-4 rounded-full px-6 py-4 items-center gap-4 flex-1">
        <LocationOnIcon />
        <input
          type="text"
          placeholder="Waypoint"
          className="flex-1 outline-none font-light"
        />
        <Trash2Icon />
      </div>
      <div className="absolute -right-8">
        <DragIndicatorIcon />
      </div>
    </div>
  );
};

const AddWaypointButton = () => {
  const SecondaryButton = importWhiteboxComponent("ui.button-secondary");
  const AddIcon = importWhiteboxComponent("icons.add");

  return (
    <div>
      <SecondaryButton
        text="Add Waypoint"
        leftIcon={<AddIcon />}
        className="w-full font-semibold"
      />
    </div>
  );
};

const FlightPlan = () => {
  const FlightLandIcon = importWhiteboxComponent("icons.flight-land");
  const FlightTakeoffIcon = importWhiteboxComponent("icons.flight-takeoff");

  return (
    <div>
      <LocationInput
        leftIcon={<FlightTakeoffIcon />}
        placeholder="Take off Location"
      />
      <WaypointInput />
      <LocationInput
        leftIcon={<FlightLandIcon />}
        placeholder="Arrival Location"
      />
      <AddWaypointButton />
    </div>
  );
};

const FlightPlanStep = () => {
  return (
    <>
      <StepIntro
        title="Flight Plan"
        description="Add some details to plan out your flight."
      />
      <FlightPlan />
    </>
  );
};

const StartFlightWizardStepWidget = ({ thisStepNumber }) => {
  const { stepNumber, setStep } = useStartFlightWizardStore();

  return (
    <div
      className={`w-full border-4 rounded-full ${
        thisStepNumber === stepNumber ? "border-gray-1" : "border-gray-5"
      }`}
      onClick={() => setStep(thisStepNumber)}
    ></div>
  );
};

const StartFlightWizardStepsWidget = () => {
  const { stepNumber, maxStepNumber } = useStartFlightWizardStore();

  return (
    <div>
      <div className="flex gap-2 mb-4 w-full">
        <StartFlightWizardStepWidget thisStepNumber={1} />
        <StartFlightWizardStepWidget thisStepNumber={2} />
        <StartFlightWizardStepWidget thisStepNumber={3} />
      </div>
      <p className="font-light text-base text-gray-2">
        Step {stepNumber} of {maxStepNumber}
      </p>
    </div>
  );
};

const StartFlightWizardContent = () => {
  const { stepNumber } = useStartFlightWizardStore();

  return (
    <div className="px-64 py-8">
      <StartFlightWizardStepsWidget />
      {stepNumber === 1 && <InstalledDevicesStep />}
      {stepNumber === 2 && <PreviewConnectedDevicesStep />}
      {stepNumber === 3 && <FlightPlanStep />}
    </div>
  );
};

const StartFlightWizardFooterNav = () => {
  const PrimaryButton = importWhiteboxComponent("ui.button-primary");
  const SecondaryButton = importWhiteboxComponent("ui.button-secondary");
  const { close, nextStep } = useStartFlightWizardStore();

  return (
    <div className="flex justify-between px-8 py-4 border-t border-gray-5">
      <SecondaryButton text="Close" onClick={close} />
      <PrimaryButton text="Next" onClick={nextStep} />
    </div>
  );
};

const StartFlightWizardFooterFinal = () => {
  const PrimaryButton = importWhiteboxComponent("ui.button-primary");
  const SecondaryButton = importWhiteboxComponent("ui.button-secondary");
  const { setCompleteLater, close } = useStartFlightWizardStore();
  const { enterFlightMode } = useMissionControlStore();

  const { toggleFlightSession } = useMissionControlStore();

  const handleStartFlight = () => {
    toggleFlightSession();
    setCompleteLater(false);
    enterFlightMode();
    close();
  };

  return (
    <div className="flex justify-between px-8 py-4 border-t border-gray-5">
      <SecondaryButton
        text="Complete later"
        onClick={() => setCompleteLater(true)}
      />
      <PrimaryButton text="Start Flight" onClick={handleStartFlight} />
    </div>
  );
};

const StartFlightWizard = ({ onClose }) => {
  const FullScreenPopOut = importWhiteboxComponent("ui.full-screen-pop-out");
  const { stepNumber, maxStepNumber } = useStartFlightWizardStore();

  return (
    <>
      <FullScreenPopOut title="Flight #010" onClose={onClose}>
        <div className="h-full flex flex-col min-h-0">
          {/* Scrollable content area */}
          <div className="flex-1 overflow-y-auto">
            <StartFlightWizardContent />
          </div>

          {/* Fixed button bar at bottom */}
          {stepNumber < maxStepNumber && <StartFlightWizardFooterNav />}
          {stepNumber === maxStepNumber && <StartFlightWizardFooterFinal />}
        </div>
      </FullScreenPopOut>
    </>
  );
};

const TriggerButton = () => {
  const { isOpen, open, close } = useStartFlightWizardStore();

  const {
    isFlightSessionActive,
    toggleFlightSession,
  } = useMissionControlStore();

  const handleClick = () => {
    if (isFlightSessionActive()) {
      toggleFlightSession();
    } else {
      open();
    }
  };

  if (!isOpen) {
    return (
      <PrimaryButton
        text={isFlightSessionActive() ? "End flight" : "Start flight"}
        className="font-semibold"
        onClick={handleClick}
      />
    );
  }

  return <StartFlightWizard onClose={close} />;
};

export { TriggerButton };
export default TriggerButton;
