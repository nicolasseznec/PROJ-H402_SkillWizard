${source_header}

#include "${objective_name}LoopFunc.h"

/****************************************/
/****************************************/

${objective_name}LoopFunction::${objective_name}LoopFunction() {
  m_ObjectiveFunction = 0;
}

/****************************************/
/****************************************/

void ${objective_name}LoopFunction::Init(argos::TConfigurationNode& t_tree){
  CoreLoopFunctions::Init(t_tree);
  ${init_function}
}

/****************************************/
/****************************************/

${objective_name}LoopFunction::${objective_name}LoopFunction(const ${objective_name}LoopFunction& orig) {}

/****************************************/
/****************************************/

${objective_name}LoopFunction::~${objective_name}LoopFunction() {}

/****************************************/
/****************************************/

void ${objective_name}LoopFunction::Destroy() {}

/****************************************/
/****************************************/

void ${objective_name}LoopFunction::Reset() {
  m_ObjectiveFunction = 0;
  CoreLoopFunctions::Reset();
  ${reset_function}
}

/****************************************/
/****************************************/

void ${objective_name}LoopFunction::PostStep() {
	m_ObjectiveFunction += ComputeStepObjectiveValue();
}

/****************************************/
/****************************************/

Real ${objective_name}LoopFunction::ComputeStepObjectiveValue() {
  ${compute_step_function}
}

/****************************************/
/****************************************/

void ${objective_name}LoopFunction::PostExperiment() {
  ${post_experiment_function}
  LOG << "${objective_name}" << std::endl;
  LOG << "Objective function result = " << m_ObjectiveFunction << std::endl;
}

/****************************************/
/****************************************/

Real ${objective_name}LoopFunction::GetObjectiveFunction() {
  return m_ObjectiveFunction;
}

/****************************************/
/****************************************/

CVector3 ${objective_name}LoopFunction::GetRandomPosition() {
  Real a;
  Real b;
  Real temp;
  ${random_position_function}
  return CVector3(fPosX, fPosY, 0);
}

/****************************************/
/****************************************/

${private_function_def}


REGISTER_LOOP_FUNCTIONS(${objective_name}LoopFunction, "${objective_name_lower}_loop_functions");