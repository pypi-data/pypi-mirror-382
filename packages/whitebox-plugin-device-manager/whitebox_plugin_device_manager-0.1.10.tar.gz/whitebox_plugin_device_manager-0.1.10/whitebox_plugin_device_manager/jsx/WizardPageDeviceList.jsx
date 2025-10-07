import ModalPage from "./common/ModalPage";
import ModalFooterButtons from "./common/ModalFooterButtons";
import useDeviceWizardStore from "./stores/device_wizard";
import { DeviceList } from "./DeviceList";

const { importWhiteboxComponent, toasts, useNavigate } = Whitebox;

// region assets
const LogoWhiteOnBlack = importWhiteboxComponent("icons.logo-white-on-black");
// endregion assets

const Heading = () => {
  return (
    <div className="flex flex-col items-center gap-4 self-stretch">
      <LogoWhiteOnBlack />

      <div
        className="flex flex-col justify-center items-center gap-2
                        self-stretch text-center"
      >
        <p className="text-2xl font-bold">Let&#39;s get you set up</p>
        <p className="text-full-emphasis text-opacity-50 leading-snug">
          To get the best experience, we recommend setting up at least one
          device. This is necessary for us to have a source to generate data.
        </p>
      </div>
    </div>
  );
};

const Footer = () => {
  const navigate = useNavigate();
  const fwdBtnHandler = useDeviceWizardStore((state) => state.nextPage);

  return (
    <div className="mt-auto">
      <ModalFooterButtons
        fwdBtn={{
          text: "Add device",
          onClick: () => fwdBtnHandler(),
        }}
        bckBtn={{
          text: "Skip",
          onClick: () => {
            toasts.info({
              message: `User decided to skip device setup at ${Date.now()}.
                      This message will expire in 5 seconds.`,
              timeout: 5,
            });
            toasts.success({
              message: "User decided to skip device setup at " + Date.now(),
            });
            toasts.error({
              message: "User decided to skip device setup at " + Date.now(),
            });
            navigate("/dashboard");
          },
        }}
        fullWidth
      />
    </div>
  );
};

const Screen = () => {
  return (
    <div className="flex flex-col h-full overflow-y-scroll-hidden">
      <div
        className="flex flex-col flex-1 self-stretch items-center
                        px-6 py-4 gap-8 overflow-y-scroll-hidden"
      >
        <Heading />
        <DeviceList />
      </div>
      <Footer />
    </div>
  );
};

const WizardPageDeviceList = () => {
  return (
    <ModalPage>
      <Screen />
    </ModalPage>
  );
};

export default WizardPageDeviceList;
