${source_header}

#ifndef ${OBJECTIVE_NAME}_LOOP_FUNC
#define ${OBJECTIVE_NAME}_LOOP_FUNC

#include <string>
#include <vector>
#include <cmath>

#include "../../src/CoreLoopFunctions.h"
#include <argos3/core/simulator/space/space.h>
#include <argos3/plugins/robots/e-puck/simulator/epuck_entity.h>
#include <argos3/plugins/simulator/entities/light_entity.h>

using namespace argos;

// Version 1
class ${objective_name}LoopFunction: public CoreLoopFunctions {
  public:
    ${objective_name}LoopFunction();
    ${objective_name}LoopFunction(const ${objective_name}LoopFunction& orig);
    virtual ~${objective_name}LoopFunction();

    virtual void Destroy();
    virtual void Reset();
    virtual void Init(argos::TConfigurationNode& t_tree);

    virtual void PostStep();
    virtual void PostExperiment();

    Real GetObjectiveFunction();

    /*
     * Returns a vector containing a random position inside a circle of radius
     * m_fDistributionRadius and centered in (0,0).
     */
    virtual CVector3 GetRandomPosition();

  private:
    virtual Real ComputeStepObjectiveValue();
    Real m_ObjectiveFunction;
${private_variables}
${private_function_decl}
};

#endif