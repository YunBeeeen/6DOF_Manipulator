# Object-Centric Vision-Language Manipulation

RGB 이미지와 자연어 명령으로 작업 대상과 공간 관계를 해석하고, ROS 2 로봇팔 제어로 연결하는 프로젝트입니다.

| 구성 | 구현 |
|---|---|
| Stage 1 | ResNet18 + Transformer 기반 객체 슬롯·위치·방향 인식 |
| Stage 2 | ColorNet 기반 슬롯 색상 분류·직접 객체 선택 |
| Stage 4 | 관계 질의와 객체 슬롯의 cross-attention을 통한 대상 선택 |
| 실행 | STT/Qwen 명령 해석, 좌표 변환, FSM·IK·궤적·그리퍼 제어 |

현재 `main`은 연구실 `feature/stage4-integration`의 최신 통합 소스를 기준으로 합니다. ROS supervisor와 MuJoCo phase 정책 실험 코드도 포함합니다. 별도로 발전한 시뮬레이션 데모는 개인 저장소의 [`upstream/good-demo-2026-07-01`](https://github.com/YunBeeeen/idle_ws/tree/upstream/good-demo-2026-07-01) 브랜치에 보존합니다.

[가져온 코드와 실행 준비](docs/UPSTREAM_INTEGRATION.md) · [인식·학습 코드](src/ml/) · [기존 로봇팔 제어](src/phy/README.md)

## 모델·데이터 준비

소스·설정·테스트를 가져왔으며 학습 이미지·가중치·캐시는 분리했습니다. 다운로드할 파일은 고정 커밋과 해시를 담은 [UPSTREAM_ASSETS.json](UPSTREAM_ASSETS.json)에서 확인할 수 있습니다.

```bash
python3 download_upstream_assets.py --group weights --list
python3 download_upstream_assets.py --group weights
python3 -m pip install -r src/ml/requirements.txt
```

ROS 2 Humble, MuJoCo, STT 및 하드웨어 의존성은 해당 모듈 문서에 따라 별도로 설치합니다. 코드의 보존·통합과 실제 로봇에서의 전체 태스크 성공 검증은 구분합니다.

---

## 기존 로봇팔 제어 문서


ROS2 (Humble) 기반 6-DoF 협동로봇 (cobot) 제어용 워크스페이스입니다. CAN 버스로 모터와 통신하고, Pinocchio 모델로 중력보상을 계산하며, MuJoCo로 시뮬레이션 시각화를 지원합니다.

## 시스템 구성

```
                    +-------------------+
                    |  사용자 입력      |  (터미널, 토픽)
                    +---------+---------+
                              |
                  /ee_target_xyz | /motor_cmd_array
                              v
+-------------+      +--------+--------+      +---------------+
|  hold_node  |      | ee_xyz_traj...  |      |  viewer_node  |
|  (중력유지) |      |  (IK + 궤적)    |      |  (MuJoCo GUI) |
+------+------+      +--------+--------+      +-------+-------+
       |                      |                       ^
       |   /motor_cmd_array   |                       |
       +----------+-----------+      /motor_state_array
                  v                                   |
            +-----+------+                            |
            | can_bridge |                            |
            |   (C++)    +----------------------------+
            +-----+------+   /motor_state_array
                  |
              CAN 0  (1 Mbps)
                  |
          +-------+--------+
          |   모터 1-6     |
          |   + 그리퍼     |
          +----------------+
```

## 패키지 구조

| 패키지 | 역할 | 언어 |
|--------|------|------|
| [idle_common](src/idle_common/) | 공통 유틸 (튜닝 YAML, 모터 매핑, 파라미터, 경로 헬퍼) | Python |
| [idle_launch](src/idle_launch/) | ROS2 launch 파일 | Python |
| [msgs](src/msgs/) | 커스텀 메시지 (`MotorCMD`, `MotorState` 등) | IDL |
| [phy](src/phy/) | 컨트롤 노드 (중력유지, EE 궤적, IK) | Python |
| [sim](src/sim/) | MuJoCo viewer + URDF + 메쉬 | Python |
| [can_interface](src/can_interface/) | CAN ↔ ROS 브리지 노드 | C++ |
| [param/](param/) | 튜닝 YAML 저장소 (`original/`, `tuned/`) | YAML |
| [motor/](motor/) | CLI 도구 (모터 enable/stop/튜닝/진단) | Python |

## 빌드

```bash
cd /home/su/idle_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

## 빠른 시작

### 1. CAN 인터페이스 활성화

```bash
sudo ip link set can0 type can bitrate 1000000
sudo ip link set can0 up
```

### 2. 노드 실행

각 노드를 별도 터미널에서:

```bash
# 터미널 1: CAN 브리지
ros2 run can_interface can_bridge_node

# 터미널 2: 중력유지 컨트롤러 + MuJoCo viewer
ros2 launch idle_launch gravity_hold.launch.py

# (선택) 터미널 3: EE 좌표 궤적 컨트롤러
ros2 run phy ee_xyz_trajectory_node
```

### 3. 모터 튜닝

```bash
# 컨트롤 노드 실행 중에도 가능 — 다음 tick에 자동 반영
cd /home/su/idle_ws/motor
python3 control_param_set.py --can_id 1 --kp 5.0 --kd 0.5
python3 control_param_save.py   # tuned/control_params.yaml 저장
```

## 주요 토픽

| 토픽 | 메시지 타입 | 방향 | 비고 |
|------|-------------|------|------|
| `/motor_state_array` | `msgs/MotorStateArray` | can_bridge → 컨트롤 노드 | 모터 피드백 (q, qd, tau) |
| `/motor_cmd_array` | `msgs/MotorCMDArray` | 컨트롤 노드 → can_bridge | MIT 모드 명령 (q_des, kp, kd, tau_ff) |
| `/motor_error_array` | `msgs/MotorErrorArray` | can_bridge → 진단 | 에러 비트 변화 이벤트 |
| `/ee_target_xyz` | `std_msgs/Float64MultiArray` | 사용자 → ee_xyz_node | EE 목표 좌표 (x, y, z) |

## 의존성

- ROS2 Humble (Ubuntu 22.04)
- Python 3.10
- pinocchio (`apt: ros-humble-pinocchio`)
- mujoco (Python wheel)
- C++17 컴파일러
- CAN 어댑터 (1 Mbps, SocketCAN)

## 협동로봇 설계 의도

이 로봇은 **외력에 자연스럽게 밀리는 협동로봇 (cobot)** 으로 설계되었습니다. 그래서:

- 250 Hz 컨트롤 루프가 중력 보상 토크를 끊김 없이 보냄
- 사람이 손으로 밀면 위치(q)가 바뀌고, 바뀐 q에 맞는 중력 토크가 자동 계산되어 부드럽게 따라감
- kp/kd는 작게 잡아 강성을 낮춤 (안전성 > 정밀도)

자세한 설계 노트는 각 패키지 README와 [param/README.md](param/README.md) 참조.

## 라이선스

Apache-2.0
