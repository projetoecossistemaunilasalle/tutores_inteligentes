#include "NexusCommandLineUtils.h"
#include "Misc/CommandLine.h" // Cabe?lho necess?io para acessar FCommandLine

FString UNexusCommandLineUtils::GetNexusRawCommandLine()
{
	// FCommandLine::Get() retorna o buffer bruto da mem?ia de inicializa?o
	return FCommandLine::Get();
}